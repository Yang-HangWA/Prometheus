###"""Pydisque makes Disque easy to access in python."""

import redis
from redis.exceptions import ConnectionError, RedisError
from functools import wraps
try:
  # Python 3
  from itertools import zip_longest
except ImportError:
  from itertools import izip_longest as zip_longest
import logging

logger = logging.getLogger(__name__)


class Job(object):

    """Represents a Disque Job."""

    def __init__(self, id, queue_name, payload):
        """Initialize a job."""
        self.id = id
        self.queue_name = queue_name
        self.payload = payload

    def __repr__(self):
        """Make a Job easy to read."""
        return '<Job id:%s queue_name:%s>' % (self.id, self.queue_name)


class Node(object):
    def __init__(self, node_id, host, port, connection):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.connection = connection

    def __repr__(self):
        """Make Node easy to read."""
        return '<Node %s:%s>' % (self.host, self.port)


class retry(object):

    """retry utility object."""

    def __init__(self, retry_count=2):
        """Initialize retry utility object."""
        self.retry_count = retry_count

    def __call__(self, fn):
        """Function wrapper."""
        @wraps(fn)
        def wrapped_f(*args, **kwargs):
            c = 0
            while c <= self.retry_count:
                try:
                    return fn(*args, **kwargs)
                except RedisError:
                    logging.critical("retrying because of this exception - %s",
                                     c)
                    logging.exception("exception to retry ")
                    if c == self.retry_count:
                        raise
                c += 1

        return wrapped_f


class Client(object):
    def __init__(self, nodes=None):
        """Initalize a client to the specified nodes."""
        if nodes is None:
            nodes = ['localhost:7711']

        self.nodes = {}
        for n in nodes:
            self.nodes[n] = None

        self.connected_node = None

    def connect(self,passwd):
    
        self.connected_node = None
        for i, node in self.nodes.items():
            host, port = i.split(':')
            port = int(port)
            redis_client = redis.Redis(host, port)
            try:
                ret = redis_client.execute_command('auth',passwd)
                format_version, node_id = ret[0], ret[1]
                others = ret[2:]
                self.nodes[i] = Node(node_id, host, port, redis_client)
                self.connected_node = self.nodes[i]
            except redis.exceptions.ConnectionError:
                pass
        if not self.connected_node:
            raise ConnectionError('couldnt connect to any nodes')
        logger.info("connected to node %s" % self.connected_node)

    def get_connection(self):
        """
        Return current connected_nodes connection.
        :rtype: redis.Redis
        """
        if self.connected_node:
            return self.connected_node.connection
        else:
            raise ConnectionError("not connected")

    @retry()
    def execute_command(self, *args, **kwargs):
        """Execute a command on the connected server."""
        try:
            return self.get_connection().execute_command(*args, **kwargs)
        except ConnectionError as e:
            logger.warn('trying to reconnect')
            self.connect()
            logger.warn('connected')
            raise

    def _grouper(self, iterable, n, fillvalue=None):
        """Collect data into fixed-length chunks or blocks."""
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)

    def info(self):
     
        return self.execute_command("INFO")

    def add_job(self, queue_name, job, timeout=200, replicate=None, delay=None,
                retry=None, ttl=None, maxlen=None, async=None):
     
        command = ['ADDJOB', queue_name, job, timeout]

        if replicate:
            command += ['REPLICATE', replicate]
        if delay:
            command += ['DELAY', delay]
        if retry is not None:
            command += ['RETRY', retry]
        if ttl:
            command += ['TTL', ttl]
        if maxlen:
            command += ['MAXLEN', maxlen]
        if async:
            command += ['ASYNC']

     
        logger.debug("sending job - %s", command)
        job_id = self.execute_command(*command)
        logger.debug("sent job - %s", command)
        logger.debug("job_id: %s " % job_id)
        return job_id

    def get_job(self, queues, timeout=None, count=None, nohang=False, withcounters=False):   
        assert queues
        command = ['GETJOB']
        if nohang:
            command += ['NOHANG']
        if timeout:
            command += ['TIMEOUT', timeout]
        if count:
            command += ['COUNT', count]
        if withcounters:
            command += ['WITHCOUNTERS']

        command += ['FROM'] + queues
        results = self.execute_command(*command)
        if not results:
            return []

        if withcounters:
            return [(job_id, queue_name, job, nacks, additional_deliveries) for
                    job_id, queue_name, job, _, nacks, _, additional_deliveries in results]
        else:
            return [(job_id, queue_name, job) for
                    job_id, queue_name, job in results]

    def ack_job(self, *job_ids):    
        self.execute_command('ACKJOB', *job_ids)

    def nack_job(self, *job_ids): 
        self.execute_command('NACK', *job_ids)

    def fast_ack(self, *job_ids):
        self.execute_command('FASTACK', *job_ids)

    def working(self, job_id):  
        return self.execute_command('WORKING', job_id)

    def qlen(self, queue_name): 
        return self.execute_command('QLEN', queue_name)

  
    def qstat(self, queue_name, return_dict=False):     
        rtn = self.execute_command('QSTAT', queue_name)
        if return_dict:
            grouped = self._grouper(rtn, 2)
            rtn = dict((a, b) for a, b in grouped)
        return rtn

    def qpeek(self, queue_name, count):
        return self.execute_command("QPEEK", queue_name, count)

    def enqueue(self, *job_ids):  
        return self.execute_command("ENQUEUE", *job_ids)

    def dequeue(self, *job_ids):   
        return self.execute_command("DEQUEUE", *job_ids)
    
    def del_job(self, *job_ids):
        return self.execute_command("DELJOB", *job_ids)

    # TODO (canardleteer): a JobStatus object may be the best for this,
    #                      but I think SHOW is going to change to SHOWJOB
    def show(self, job_id, return_dict=False):
        rtn = self.execute_command('SHOW', job_id)
        if return_dict:
            grouped = self._grouper(rtn, 2)
            rtn = dict((a, b) for a, b in grouped)

        return rtn

    def pause(self, queue_name, kw_in=None, kw_out=None, kw_all=None,
              kw_none=None, kw_state=None, kw_bcast=None):
        command = ["PAUSE", queue_name]
        if kw_in:
            command += ["in"]
        if kw_out:
            command += ["out"]
        if kw_all:
            command += ["all"]
        if kw_none:
            command += ["none"]
        if kw_state:
            command += ["state"]
        if kw_bcast:
            command += ["bcast"]

        return self.execute_command(*command)

    def qscan(self, cursor=0, count=None, busyloop=None, minlen=None,
              maxlen=None, importrate=None):
        command = ["QSCAN", cursor]
        if count:
            command += ["COUNT", count]
        if busyloop:
            command += ["BUSYLOOP"]
        if minlen:
            command += ["MINLEN", minlen]
        if maxlen:
            command += ["MAXLEN", maxlen]
        if importrate:
            command += ["IMPORTRATE", importrate]

        return self.execute_command(*command)

    def jscan(self, cursor=0, count=None, busyloop=None, queue=None,
              state=None, reply=None):
        command = ["JSCAN", cursor]
        if count:
            command += ["COUNT", count]
        if busyloop:
            command += ["BUSYLOOP"]
        if queue:
            command += ["QUEUE", queue]
        if type(state) is list:
            for s in state:
                command += ["STATE", s]
        if reply:
            command += ["REPLY", reply]

        return self.execute_command(*command)

    def show(self, job_id, return_dict=False):     
        rtn = self.execute_command('SHOW', job_id)
        if return_dict:
            grouped = self._grouper(rtn, 2)
            rtn = dict((a, b) for a, b in grouped)

        return rtn

    def hello(self):  
        return self.execute_command("HELLO")




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    c = Client(['localhost:7712', 'localhost:7711'])
    c.connect("penetration")
    print c.info()

    # while True:
    #     jobs = c.get_job(['test'], timeout=5)

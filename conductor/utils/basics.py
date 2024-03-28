import datetime
import glob
import logging
import os
import threading

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir, 'log')


class TopLogST:
    _inst_lock = threading.Lock()
    _log_out_file = ''

    def __new__(cls, *args, **kwargs):
        with TopLogST._inst_lock:
            if not hasattr(cls, '_instance'):
                TopLogST._instance = super().__new__(cls)
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
                now = datetime.datetime.now()
                trace_time = now.strftime("%Y-%m-%d_%H-%M-%S")
                setattr(cls, '_log_out_file', os.path.join(log_dir, ('log_%s.log' % str(trace_time))))
        return TopLogST._instance

    @staticmethod
    def _cleanup_log_files(log_dir):
        log_files = glob.glob(os.path.join(log_dir, "log_*.log"))
        if len(log_files) >= 15:
            log_files.sort()
            for i in range(len(log_files) - 15):
                os.remove(log_files[i])

    def get_logger(self, name):
        self._cleanup_log_files(log_dir)
        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
        fh = logging.FileHandler(self._log_out_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        return logger


def get_logger(name):
    return TopLogST().get_logger(name)


if __name__ == '__main__':
    logger = get_logger('test')
    logger.warning('test')

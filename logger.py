import time
import logging
import config

# ---------------- Set up logger for writing logs


def setup_logger(name, log_file, level=logging.INFO, add_time='yes'):
		"""Function setup as many loggers as you want"""

		formatter = logging.Formatter(
				'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		logging.Formatter.converter = time.gmtime

		path = config.path_logs

		if add_time == 'yes':
				hour = time.strftime("%m-%d_%H", time.gmtime(time.time()))+'_'
		else:
				hour = '001_'

		handler = logging.FileHandler(path+hour+log_file+'.log')
		handler.setFormatter(formatter)

		logger = logging.getLogger(name)
		logger.setLevel(level)
		logger.addHandler(handler)

		return logger
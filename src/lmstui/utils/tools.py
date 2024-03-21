import datetime, logging, math

from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

def convert_bytesize(size_bytes):
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return "%s %s" % (s, size_name[i])

def seconds2str( secs):
	hours, remainder = divmod( secs, 3600)
	minutes, seconds = divmod(remainder, 60)
	if hours > 0:
		return "{}:{:02}:{:02}".format( int(hours), int( minutes), int( seconds))
	else:
		return "{:02}:{:02}".format( int( minutes), int( seconds))
	#return str( datetime.timedelta(seconds=round(secs)))

def rating2icon( rating):
	#_LOGGER.debug( "rating2icon {}".format( rating))
	if rating in range( 20, 40):
		return config.ICON_thermometer_0
	elif rating in range( 40, 60):
		return config.ICON_thermometer_1
	elif rating in range( 60, 80):
		return config.ICON_thermometer_2
	elif rating in range( 80, 100):
		return config.ICON_thermometer_3
	elif rating >= 100:
		return config.ICON_thermometer_4
	else:
		return config.ICON_question

def progressbar( value, length=16, vmin=0.0, vmax=1.0, lsep="▏", rsep="▕"):
	blocks = [ "", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
	vmin = vmin or 0.0
	vmax = vmax or 1.0
	#lsep, rsep = "▏", "▕"

	# Normalize value
	value = min(max(value, vmin), vmax)
	value = ( value - vmin) / float( vmax - vmin)

	v = value * length
	x = math.floor(v)  # integer part
	y = v - x          # fractional part
	'''
	base = 0.125      # 0.125 = 1/8
	prec = 3
	i = int(round(base*math.floor(float(y)/base),prec)/base)
	'''
	i = int(round( y * 8))
	bar = "█" * x + blocks[i]
	n = length - len(bar)
	bar = lsep + bar + " " * n + rsep
	return bar

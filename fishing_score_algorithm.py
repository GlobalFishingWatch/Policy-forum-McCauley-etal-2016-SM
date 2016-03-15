# Set up some temporary fields
tmpfields = ['measure_speed', 'measure_course','measure_speedstddev_3600','measure_speedavg_3600','measure_coursestddev_3600','measure_score_3600']
x = append_fields(x, tmpfields, [[]]*len(tmpfields), dtypes='<f8', fill_value=0.0)

# Normalize speed and heading
speed = x['speed'] / 17.0
x['measure_speed'] = 1 - where(speed > 1.0, 1.0, speed)
x['measure_course'] = x['course'] / 360.0

windowSize = 3600

# Sort by mmsi, then by timestamp
x = x[lexsort((x['timestamp'], x['mmsi']))]

# Calculate rolling stddev/avg of course and speed
start_idx = 0
for end_idx in xrange(0, x.shape[0]):
    while (x['mmsi'][start_idx] != x['mmsi'][end_idx]
           or x['timestamp'][start_idx] < x['timestamp'][end_idx] - windowSize):
        start_idx += 1
    assert start_idx <= end_idx
    window = x[start_idx:end_idx + 1]   
    x['measure_speedstddev_3600'][end_idx] = window['measure_speed'].std()
    x['measure_speedavg_3600'][end_idx] = numpy.average(window['measure_speed'])
    x['measure_coursestddev_3600'][end_idx] = window['measure_course'].std()

# Average with expermentally determined *2 scaling
score = (x['measure_coursestddev_3600'] + x['measure_speedstddev_3600'] + x['measure_speedavg_3600']) * 2.0 / 3.0

# Clamp to ]0, 1[
score = where(score < 0.0, 0.0, where(score > 1.0, 1.0, score))

# Port behavior is hard to distinguish from fishing, so supress score close to shore...
x['measure_score_3600'] = where(x['distance_to_shore'] < 3, 0.0, score)

#Author: Egil Moeller <egil@skytruth.org>

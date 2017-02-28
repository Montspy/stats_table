import argparse
import numpy as np
import pprint
import os

# python stat_table.py -es 65 100 110 69 62 -ss 25 22 22 19 18 -c druid

def eval_poly(x, c):
	return np.polyval(c, x)

def eval_exp(x, c):
	return c[0] + c[1]*np.exp(c[2]*x)

def calculateStat(budget, partition):
	return np.around(partition * budget)

parser = argparse.ArgumentParser(description='Generates stats table from curve and end level stats')

curve_group = parser.add_mutually_exclusive_group()
curve_group.add_argument("-p", "--poly", type=np.float_, nargs='+', metavar=('an', 'an-1'), 
                    help="uses a custom n degree polynomial curve for budget vs level")
curve_group.add_argument("-e", "--exp", type=np.float_, nargs=3, metavar=('k', 'a', 'l'),
                    help="uses a custom exponential curve for budget vs level (y = k + a*exp(l*x))")
parser.add_argument("-es", "--endstats", type=np.float_, required=True, nargs=5, metavar=('agi', 'int', 'spi', 'stam', 'str'), 
					help="end level stats")
parser.add_argument("-ss", "--startstats", type=np.float_, nargs=5, metavar=('agi', 'int', 'spi', 'stam', 'str'), 
					help="start stats")
parser.add_argument("-c", "--comment", 
                    help="filename comment")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

args = parser.parse_args()
    
r = {}
stat_names = ('agi', 'int', 'spi', 'sta', 'str')
default_coef_exp = (-0.881406, 0.868759, 0.0128872)	# Exponential from RoadBlock, normalized to lvl 60

r['comment'] = ''
if args.comment is not None:
	r['comment'] = args.comment

# Get curve function and coefficients
eval_curve = eval_exp
r['coefs'] = default_coef_exp
if args.poly is not None:
	eval_curve = args.poly
	r['coefs'] = args.poly
elif args.exp is not None:
	eval_curve = eval_exp
	r['coefs'] = args.exp


# Get start stats if given, otherwise assume 0 all across
r['start_stats'] = np.zeros(5).astype(np.float_)
if args.startstats is not None:
	r['start_stats'] = np.asarray(args.startstats).astype(np.float_)
	
# Get stats, end level budget and partition
r['end_stats'] = np.asarray(args.endstats).astype(np.float_)
r['end_budget'] = np.sum(r['end_stats']-r['start_stats'])
r['partition'] = np.array(r['end_stats']-r['start_stats'])/r['end_budget']

if args.verbose:
	print('eval_curve', eval_curve)
	pprint.pprint(r)

# Generate budget (1 to 60), and split stats based on partition
r['levels'] = np.array(range(1, 61))
r['budget'] = np.zeros_like(r['levels']).astype(np.float_);
for sn in stat_names:
	r[sn] = np.zeros(60)

for l in r['levels']:
	r['budget'][l-1] = eval_curve(l, r['coefs'])*r['end_budget']
	stats = calculateStat(r['budget'][l-1], r['partition']) + r['start_stats']
	
	for i, sn in enumerate(stat_names):
		r[sn][l-1] = stats[i]

if args.verbose:
	pprint.pprint(r)

# Save to CSV file
all_stats = r['agi']
for sn in stat_names[1:]:
	all_stats = np.vstack((all_stats, r[sn]))

if not os.path.exists('stats'):
    os.makedirs('stats')
filename = 'stats/' + r['comment'] + '.csv'
np.savetxt(filename, np.transpose(all_stats), fmt='%d', delimiter=',', newline='\n', header=','.join(stat_names), comments='')

# Print out to console
row_format ="{:>15}" * (len(stat_names))
print row_format.format(*stat_names)
print np.transpose(all_stats).shape
for stats in np.transpose(all_stats):
    print row_format.format(*stats)

print('Done!')


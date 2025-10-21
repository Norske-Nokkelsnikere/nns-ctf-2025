from pyjls import Reader
import numpy as np
import scipy as sp
path = '../handout/chall.jls'

# Load Joulescope current data
with Reader(path) as r:
    signal = r.signal_lookup('current')
    data = r.fsr(signal.signal_id, 0, signal.length) 

    print("Loaded signal")


# Data are sampled at 2 MHz. This is higher than needed.
data = sp.signal.decimate(data, 20)

# Filter to remove small peaks that may be falsely detected as periods of high current
coeffs = sp.signal.firwin(100, 1000, fs=100000, window="hann")
data = sp.signal.lfilter(coeffs, 1.0, data)
print("Computed filered signal")

# Find the periods where the current is above 5 mA
threshold = 5e-3

time = [0]
val = [0]
onelengths = []

for i, s in enumerate(data):
    curr = s > threshold

    if val[-1] != curr:
        if not curr:
            onelengths.append(i - time[-1])

        val.append(not curr)
        time.append(i)
        val.append(curr)
        time.append(i)

time.append(len(data))
val.append(val[-1])
print("Computed threshold changes")

# The first peaks are due to other activity, discard
onelengths = onelengths[3:]

# Require 1300 / (100 kHz) = 13 ms to be detected as a long period (i.e. a high bit)
thresh = 1300

onelengths_dig = [x > thresh for x in onelengths]

# Convert bits to int
d_calc = int.from_bytes(bytes(np.packbits(onelengths_dig, bitorder="little")), "little")

# RSA parameters from handouts
n = 13664239037907372261661891470992995812128631528934391124752884269617528651053943317643090937575784947507121014497497717171715238000721198283113013794512130295734489576260331261682561465391758930638013357402072021478110973654128826298049766903982395037335779141190402313347639858098129949466177493850907993591446653720099179365990534644620448650304131652280474041746240378613910471399168587342852511744545430231691608897504605714598606184911482705356693806768783646940958690855586096924000403615689800819397967604105338773209636756859376501323800107361614560297027162314856937948699650209286373343705091388728140792503
c = 7017475957803874462523966074302543158129097147429790657226279960682896591477226122698282095738274246721238318890653196205916830216637458496892522095257681715003618677124495890023843861343165641630855514175553150271337745667046395825325665199881603875814091318619655247836156484392842577721656378956876207867313374046749934094115294456504848029102891923490159831053984238123331848687881208689685500800642357139091392163908410372967220411143432404551854426595259687401994837786183518387073808919815886349474945163639093802074478297811137406107429230463524738469120697169759618786129980489550678589429921447071806277046

# The first 1 bit will look like a 0. The call to mp_mul(result, base, result); will not be short, since result will be 1 until a 1 bit has been encountered
# The first 1 bit must be bruteforced

for i in range(2048):
    d = d_calc | (1 << i)
    
    flag_number = pow(c, d, n)

    flag = flag_number.to_bytes(256, "little").decode("utf-8", errors="ignore")

    if flag.startswith("NNS{"):
        print(f"Found flag: {flag}")
        break

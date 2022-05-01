from poker import Range, Combo
import time
all_combos = list(Range('XX').combos)
print(all_combos)
all_combos.sort()
print(len(all_combos))
t1 = time.time()
print(Combo('AhKd') in all_combos)
t2 = time.time()
print(t2 - t1)
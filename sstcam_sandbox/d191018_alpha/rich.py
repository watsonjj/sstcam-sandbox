
m1 = 1.0
m2 = 0.5 * m1
rb = 2. * m2 **2
rs = 0.01 * m2 **2

alpha = 0.2

# Within alpha cut (6 degree)
# rs_old = 0.005680752347925706
# rs_new = 0.014111445248979046
# rb_old = 2.170441445814701
# rb_new = 10.62473792261415
# ron_old = 0.44064638032031767
# ron_new = 2.209307488877769

# Within alpha cut (5 degree)
rs_old = 0.005161440800396995
rs_new = 0.012790648595259909
rb_old = 1.8120502171336377
rb_new = 8.843901753068339
ron_old = 0.36970412637281214
ron_new = 1.8250662767809671

# Total
# rs_old = 0.009112604796513607
# rs_new = 0.02300757237373318
# rb_old = 33.44384818200358
# rb_new = 160.55342114352885
# ron_old = 6.6887696364007105
# ron_new = 32.11068422870587

print(rb_old * alpha, ron_old, ron_old - rb_old * alpha)
print(rb_new * alpha, ron_new, ron_new - rb_new * alpha)
print((ron_new - rb_new * alpha) / (ron_old - rb_old * alpha))
print(ron_new / ron_old)
print(rs_new / rs_old)
print(rb_new / rb_old)



print((rs_new * m2) ** 2/ rs_old)
print((rb_new * m2) ** 2/ rb_old)


import numpy as np
from numpy.polynomial.polynomial import polyfit

def li_ma(n_on, n_off, alpha):
    return np.sqrt(2) * np.sqrt(
        n_on * np.log(
            ((1+alpha)/alpha) * (n_on/(n_on+n_off))
        ) +
        n_off * np.log(
            (1+alpha) * (n_off/(n_on+n_off))
        )
    )
time = np.linspace(1, 2*24*60*60, 1000)

n_on = ((rs_old * 1.25) + (rb_old * 2.5 * alpha)) * time
n_off = (rb_old * 2.5) * time

n_on = (rs_new + rb_new * alpha) * time
n_off = (rb_new) * time

n_on = (ron_new) * time
n_off = (rb_new) * time


print(rs_new + rb_new * alpha, ron_new)

significance = li_ma(n_on, n_off, alpha)
_, sig_per_sqrthour = polyfit(np.sqrt(time / 3600), significance, [1])
print(f'sig_per_sqrthour={sig_per_sqrthour}')
n_hours = (5/sig_per_sqrthour)**2
print(f'n_hours={n_hours}')
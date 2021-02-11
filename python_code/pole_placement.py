import numpy as np

Krpm = 48 # RPM/V
Krads = Krpm * 0.104719755
tau = 0.050 #seconds

emax = 250 #rpm
emax_rads = 250 * 0.104719755

umax = 12

kp = umax/emax_rads # Vs/rad

zeta = 0.7

omega_n = (Krads*kp + 1) / (tau*2*zeta)

ki = (omega_n**2)*tau/Krads

print('Krads', Krads)
print('omega_n', omega_n)
print('kp_rad', kp)
print('ki_rad', ki)
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

applied_force_radius = 08.25 #centimeters

pwm_to_volts_stalled = np.zeros(shape=(14,2))
pwm_to_current_stalled = np.zeros(shape=(14,2))
pwm_to_current_inertia = np.zeros(shape=(14,2))
pwm_to_ang_vel = np.zeros(shape=(14,2))
pwm_to_torque = np.zeros(shape=(14,2))

#print(pwm_to_volts_stalled)

# NB: All calculations were done with motor rotating CCW (digitalWrite(DIR_B, LOW))
# Note: All of the 6 below lists have a 0 appended at the end of it
pwms = [255, 240, 230, 220, 200, 180, 160, 140, 120, 100, 80, 60, 40, 0] 
volts_theoretical = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
vavg_stalled = [9.92,9.22,8.39,7.51,6.70,5.83,5.10,4.36,3.49,2.65,1.75,0.84]
vrms_stalled = [9.92, 9.53, 9.35, 9.31, 9.02, 8.72, 8.38,7.82, 6.95,6.09,5.52, 4.85, 4.04,0]
current_stalled =       [0.724, 0.621, 0.575, 0.515, 0.388, 0.262, 0.217, 0.174, 0.137, 0.101, 0.068, 0.048, 0.021,0]
current_inertia_wheel = [0.027, 0.025, 0.025, 0.025, 0.025, 0.024, 0.023, 0.023, 0.023, 0.022, 0.021, 0.019, 0.015,0]
ang_vel = [52.48, 50.2, 50.05, 49.3, 48.58, 47.48, 45.78, 44.00, 40.55, 36.56, 30.85, 21.35, 6.55,0]
forces = [92.4, 95, 80, 70,57.7, 52, 46, 39, 31.4, 25.5,19.5, 12.5, 7,0] #grams



# Linear Regression For Loop
all_lists = [vrms_stalled, current_stalled, current_inertia_wheel, ang_vel, forces]
pwms_numpy = np.array(pwms)
pwms_numpy = pwms_numpy.reshape(-1,1)

y_predicted = [None] * 5
y_beta = [None] * 5
y_intercept = [None] * 5


for i in range(5):
    val = np.array(all_lists[i])
    linreg = LinearRegression()
    linreg.fit(pwms_numpy,val)
    prediction = linreg.predict(pwms_numpy)
    y_predicted[i] = prediction
    y_beta[i] = linreg.coef_
    y_intercept[i] = linreg.intercept_

y_beta[4] = y_beta[4]*applied_force_radius/1000
y_intercept[4] = y_intercept[4]*applied_force_radius/1000


degree = 2

polyreg2 = make_pipeline(PolynomialFeatures(degree),LinearRegression())
polyreg2.fit(pwms_numpy,all_lists[2])
prediction2 = polyreg2.predict(pwms_numpy)
y_predicted[2] = prediction2
"""
prediction2_beta = polyreg2.coef_
prediction2_intercept = polyreg2.intercept_
"""

polyreg3 = make_pipeline(PolynomialFeatures(degree),LinearRegression())
polyreg3.fit(pwms_numpy,all_lists[3])
prediction3 = polyreg3.predict(pwms_numpy)
y_predicted[3] = prediction3
"""
prediction3_beta = polyreg3.coef_
prediction3_intercept = polyreg3.intercept_
"""

for i, val in enumerate(pwms):
    pwm_to_volts_stalled[i][0] = pwms[i]
    pwm_to_volts_stalled[i][1] = vrms_stalled[i]

    pwm_to_current_stalled[i][0] = pwms[i]
    pwm_to_current_stalled[i][1] = current_stalled[i]

    pwm_to_current_inertia[i][0] = pwms[i]
    pwm_to_current_inertia[i][1] = current_inertia_wheel[i]

    pwm_to_ang_vel[i][0] = pwms[i]
    pwm_to_ang_vel[i][1] = ang_vel[i]

    pwm_to_torque[i][0] = pwms[i]
    pwm_to_torque[i][1] = forces[i]*applied_force_radius/1000

#print(pwm_to_volts_stalled)

#Plotting
# fig, axes = plt.subplots(5)
plt.figure(1)
plt.plot(volts_theoretical, vavg_stalled, color='blue', linewidth=1)
# axes[0].plot(pwms_numpy, y_predicted[0], color='black', linewidth=1, label=f"{y_beta[0][0].round(3)}x+{y_intercept[0].round(3)}")
plt.ylabel("V_avg_stalled")
plt.xlabel("V_applied_in_GUI")
plt.title("V_theoretical vs V_across_motor")

# axes[1].plot(pwm_to_current_stalled[:,0], pwm_to_current_stalled[:,1], color='red', linewidth=1)
# # axes[1].plot(pwms_numpy, y_predicted[1], color='black', linewidth=1, label=f"{y_beta[1][0].round(3)}x+{y_intercept[1].round(3)}")
# axes[1].legend()

# axes[2].plot(pwm_to_current_inertia[:,0], pwm_to_current_inertia[:,1], color='green', linewidth=1)
# # axes[2].plot(pwms_numpy, y_predicted[2], color='black', linewidth=1)#, label=f"{y_beta[2][0].round(10)}x+{y_intercept[2].round(3)}")
# #axes[2].legend()


# axes[3].plot(pwm_to_ang_vel[:,0], pwm_to_ang_vel[:,1], color='orange', linewidth=1)
# # axes[3].plot(pwms_numpy, y_predicted[3], color='black', linewidth=1)#, label=f"{y_beta[3][0].round(3)}x+{y_intercept[3].round(3)}")
# #axes[3].legend()


# axes[4].plot(pwm_to_torque[:,0], pwm_to_torque[:,1], color='cyan', linewidth=1)
# # axes[4].plot(pwms_numpy, y_predicted[4]*applied_force_radius/1000, color='black', linewidth=1, label=f"{y_beta[4][0].round(3)}x+{y_intercept[4].round(3)}")
# axes[4].legend()


# for a in axes:
#     a.set(xlabel='pwm')
# axes[0].set(ylabel='V_rms')
# axes[1].set(ylabel='stalled current (A_rms)')
# axes[2].set(ylabel='rotating current (A_rms)')
# axes[3].set(ylabel='ang_vel (rad/sec)')
# axes[4].set(ylabel='torques (kg*cm)')
plt.show()
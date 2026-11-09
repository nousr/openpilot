#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_6506715188500082950);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7066564298617859979);
void car_H_mod_fun(double *state, double *out_7075167101777140118);
void car_f_fun(double *state, double dt, double *out_6100346516483839845);
void car_F_fun(double *state, double dt, double *out_6723015174263675602);
void car_h_25(double *state, double *unused, double *out_3834518551131794938);
void car_H_25(double *state, double *unused, double *out_7848596321942919821);
void car_h_24(double *state, double *unused, double *out_5358348446771717581);
void car_H_24(double *state, double *unused, double *out_4290670723140596685);
void car_h_30(double *state, double *unused, double *out_2936316675218555998);
void car_H_30(double *state, double *unused, double *out_6070451421639023597);
void car_h_26(double *state, double *unused, double *out_6714117934224998478);
void car_H_26(double *state, double *unused, double *out_6856644432892575571);
void car_h_27(double *state, double *unused, double *out_4437834435808272455);
void car_H_27(double *state, double *unused, double *out_8294045492822966814);
void car_h_29(double *state, double *unused, double *out_1986884048044984833);
void car_H_29(double *state, double *unused, double *out_6580682765953415781);
void car_h_28(double *state, double *unused, double *out_2818309281285179254);
void car_H_28(double *state, double *unused, double *out_8544313037518742032);
void car_h_31(double *state, double *unused, double *out_886792560776309977);
void car_H_31(double *state, double *unused, double *out_7817950360065959393);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}
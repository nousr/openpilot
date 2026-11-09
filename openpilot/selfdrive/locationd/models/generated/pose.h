#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_390439054689636793);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7990457038845758323);
void pose_H_mod_fun(double *state, double *out_228771635186623352);
void pose_f_fun(double *state, double dt, double *out_995521470232249249);
void pose_F_fun(double *state, double dt, double *out_8885441589559760893);
void pose_h_4(double *state, double *unused, double *out_7395363253468584448);
void pose_H_4(double *state, double *unused, double *out_9173133301244444694);
void pose_h_10(double *state, double *unused, double *out_5791319130957704786);
void pose_H_10(double *state, double *unused, double *out_8382500807432592143);
void pose_h_13(double *state, double *unused, double *out_8786519752124647312);
void pose_H_13(double *state, double *unused, double *out_5960859475912111893);
void pose_h_14(double *state, double *unused, double *out_7337444961737170917);
void pose_H_14(double *state, double *unused, double *out_1792464957185366498);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}
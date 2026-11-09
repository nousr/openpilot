#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_6506715188500082950) {
   out_6506715188500082950[0] = delta_x[0] + nom_x[0];
   out_6506715188500082950[1] = delta_x[1] + nom_x[1];
   out_6506715188500082950[2] = delta_x[2] + nom_x[2];
   out_6506715188500082950[3] = delta_x[3] + nom_x[3];
   out_6506715188500082950[4] = delta_x[4] + nom_x[4];
   out_6506715188500082950[5] = delta_x[5] + nom_x[5];
   out_6506715188500082950[6] = delta_x[6] + nom_x[6];
   out_6506715188500082950[7] = delta_x[7] + nom_x[7];
   out_6506715188500082950[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7066564298617859979) {
   out_7066564298617859979[0] = -nom_x[0] + true_x[0];
   out_7066564298617859979[1] = -nom_x[1] + true_x[1];
   out_7066564298617859979[2] = -nom_x[2] + true_x[2];
   out_7066564298617859979[3] = -nom_x[3] + true_x[3];
   out_7066564298617859979[4] = -nom_x[4] + true_x[4];
   out_7066564298617859979[5] = -nom_x[5] + true_x[5];
   out_7066564298617859979[6] = -nom_x[6] + true_x[6];
   out_7066564298617859979[7] = -nom_x[7] + true_x[7];
   out_7066564298617859979[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7075167101777140118) {
   out_7075167101777140118[0] = 1.0;
   out_7075167101777140118[1] = 0.0;
   out_7075167101777140118[2] = 0.0;
   out_7075167101777140118[3] = 0.0;
   out_7075167101777140118[4] = 0.0;
   out_7075167101777140118[5] = 0.0;
   out_7075167101777140118[6] = 0.0;
   out_7075167101777140118[7] = 0.0;
   out_7075167101777140118[8] = 0.0;
   out_7075167101777140118[9] = 0.0;
   out_7075167101777140118[10] = 1.0;
   out_7075167101777140118[11] = 0.0;
   out_7075167101777140118[12] = 0.0;
   out_7075167101777140118[13] = 0.0;
   out_7075167101777140118[14] = 0.0;
   out_7075167101777140118[15] = 0.0;
   out_7075167101777140118[16] = 0.0;
   out_7075167101777140118[17] = 0.0;
   out_7075167101777140118[18] = 0.0;
   out_7075167101777140118[19] = 0.0;
   out_7075167101777140118[20] = 1.0;
   out_7075167101777140118[21] = 0.0;
   out_7075167101777140118[22] = 0.0;
   out_7075167101777140118[23] = 0.0;
   out_7075167101777140118[24] = 0.0;
   out_7075167101777140118[25] = 0.0;
   out_7075167101777140118[26] = 0.0;
   out_7075167101777140118[27] = 0.0;
   out_7075167101777140118[28] = 0.0;
   out_7075167101777140118[29] = 0.0;
   out_7075167101777140118[30] = 1.0;
   out_7075167101777140118[31] = 0.0;
   out_7075167101777140118[32] = 0.0;
   out_7075167101777140118[33] = 0.0;
   out_7075167101777140118[34] = 0.0;
   out_7075167101777140118[35] = 0.0;
   out_7075167101777140118[36] = 0.0;
   out_7075167101777140118[37] = 0.0;
   out_7075167101777140118[38] = 0.0;
   out_7075167101777140118[39] = 0.0;
   out_7075167101777140118[40] = 1.0;
   out_7075167101777140118[41] = 0.0;
   out_7075167101777140118[42] = 0.0;
   out_7075167101777140118[43] = 0.0;
   out_7075167101777140118[44] = 0.0;
   out_7075167101777140118[45] = 0.0;
   out_7075167101777140118[46] = 0.0;
   out_7075167101777140118[47] = 0.0;
   out_7075167101777140118[48] = 0.0;
   out_7075167101777140118[49] = 0.0;
   out_7075167101777140118[50] = 1.0;
   out_7075167101777140118[51] = 0.0;
   out_7075167101777140118[52] = 0.0;
   out_7075167101777140118[53] = 0.0;
   out_7075167101777140118[54] = 0.0;
   out_7075167101777140118[55] = 0.0;
   out_7075167101777140118[56] = 0.0;
   out_7075167101777140118[57] = 0.0;
   out_7075167101777140118[58] = 0.0;
   out_7075167101777140118[59] = 0.0;
   out_7075167101777140118[60] = 1.0;
   out_7075167101777140118[61] = 0.0;
   out_7075167101777140118[62] = 0.0;
   out_7075167101777140118[63] = 0.0;
   out_7075167101777140118[64] = 0.0;
   out_7075167101777140118[65] = 0.0;
   out_7075167101777140118[66] = 0.0;
   out_7075167101777140118[67] = 0.0;
   out_7075167101777140118[68] = 0.0;
   out_7075167101777140118[69] = 0.0;
   out_7075167101777140118[70] = 1.0;
   out_7075167101777140118[71] = 0.0;
   out_7075167101777140118[72] = 0.0;
   out_7075167101777140118[73] = 0.0;
   out_7075167101777140118[74] = 0.0;
   out_7075167101777140118[75] = 0.0;
   out_7075167101777140118[76] = 0.0;
   out_7075167101777140118[77] = 0.0;
   out_7075167101777140118[78] = 0.0;
   out_7075167101777140118[79] = 0.0;
   out_7075167101777140118[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6100346516483839845) {
   out_6100346516483839845[0] = state[0];
   out_6100346516483839845[1] = state[1];
   out_6100346516483839845[2] = state[2];
   out_6100346516483839845[3] = state[3];
   out_6100346516483839845[4] = state[4];
   out_6100346516483839845[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_6100346516483839845[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6100346516483839845[7] = state[7];
   out_6100346516483839845[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6723015174263675602) {
   out_6723015174263675602[0] = 1;
   out_6723015174263675602[1] = 0;
   out_6723015174263675602[2] = 0;
   out_6723015174263675602[3] = 0;
   out_6723015174263675602[4] = 0;
   out_6723015174263675602[5] = 0;
   out_6723015174263675602[6] = 0;
   out_6723015174263675602[7] = 0;
   out_6723015174263675602[8] = 0;
   out_6723015174263675602[9] = 0;
   out_6723015174263675602[10] = 1;
   out_6723015174263675602[11] = 0;
   out_6723015174263675602[12] = 0;
   out_6723015174263675602[13] = 0;
   out_6723015174263675602[14] = 0;
   out_6723015174263675602[15] = 0;
   out_6723015174263675602[16] = 0;
   out_6723015174263675602[17] = 0;
   out_6723015174263675602[18] = 0;
   out_6723015174263675602[19] = 0;
   out_6723015174263675602[20] = 1;
   out_6723015174263675602[21] = 0;
   out_6723015174263675602[22] = 0;
   out_6723015174263675602[23] = 0;
   out_6723015174263675602[24] = 0;
   out_6723015174263675602[25] = 0;
   out_6723015174263675602[26] = 0;
   out_6723015174263675602[27] = 0;
   out_6723015174263675602[28] = 0;
   out_6723015174263675602[29] = 0;
   out_6723015174263675602[30] = 1;
   out_6723015174263675602[31] = 0;
   out_6723015174263675602[32] = 0;
   out_6723015174263675602[33] = 0;
   out_6723015174263675602[34] = 0;
   out_6723015174263675602[35] = 0;
   out_6723015174263675602[36] = 0;
   out_6723015174263675602[37] = 0;
   out_6723015174263675602[38] = 0;
   out_6723015174263675602[39] = 0;
   out_6723015174263675602[40] = 1;
   out_6723015174263675602[41] = 0;
   out_6723015174263675602[42] = 0;
   out_6723015174263675602[43] = 0;
   out_6723015174263675602[44] = 0;
   out_6723015174263675602[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_6723015174263675602[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_6723015174263675602[47] = -dt*stiffness_front*state[0]/state[1];
   out_6723015174263675602[48] = -dt*stiffness_front*state[0]/state[1];
   out_6723015174263675602[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_6723015174263675602[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_6723015174263675602[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_6723015174263675602[52] = dt*stiffness_front*state[0]/state[1];
   out_6723015174263675602[53] = -9.8100000000000005*dt;
   out_6723015174263675602[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6723015174263675602[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6723015174263675602[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6723015174263675602[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6723015174263675602[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6723015174263675602[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6723015174263675602[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6723015174263675602[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6723015174263675602[62] = 0;
   out_6723015174263675602[63] = 0;
   out_6723015174263675602[64] = 0;
   out_6723015174263675602[65] = 0;
   out_6723015174263675602[66] = 0;
   out_6723015174263675602[67] = 0;
   out_6723015174263675602[68] = 0;
   out_6723015174263675602[69] = 0;
   out_6723015174263675602[70] = 1;
   out_6723015174263675602[71] = 0;
   out_6723015174263675602[72] = 0;
   out_6723015174263675602[73] = 0;
   out_6723015174263675602[74] = 0;
   out_6723015174263675602[75] = 0;
   out_6723015174263675602[76] = 0;
   out_6723015174263675602[77] = 0;
   out_6723015174263675602[78] = 0;
   out_6723015174263675602[79] = 0;
   out_6723015174263675602[80] = 1;
}
void h_25(double *state, double *unused, double *out_3834518551131794938) {
   out_3834518551131794938[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7848596321942919821) {
   out_7848596321942919821[0] = 0;
   out_7848596321942919821[1] = 0;
   out_7848596321942919821[2] = 0;
   out_7848596321942919821[3] = 0;
   out_7848596321942919821[4] = 0;
   out_7848596321942919821[5] = 0;
   out_7848596321942919821[6] = 1;
   out_7848596321942919821[7] = 0;
   out_7848596321942919821[8] = 0;
}
void h_24(double *state, double *unused, double *out_5358348446771717581) {
   out_5358348446771717581[0] = state[4];
   out_5358348446771717581[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4290670723140596685) {
   out_4290670723140596685[0] = 0;
   out_4290670723140596685[1] = 0;
   out_4290670723140596685[2] = 0;
   out_4290670723140596685[3] = 0;
   out_4290670723140596685[4] = 1;
   out_4290670723140596685[5] = 0;
   out_4290670723140596685[6] = 0;
   out_4290670723140596685[7] = 0;
   out_4290670723140596685[8] = 0;
   out_4290670723140596685[9] = 0;
   out_4290670723140596685[10] = 0;
   out_4290670723140596685[11] = 0;
   out_4290670723140596685[12] = 0;
   out_4290670723140596685[13] = 0;
   out_4290670723140596685[14] = 1;
   out_4290670723140596685[15] = 0;
   out_4290670723140596685[16] = 0;
   out_4290670723140596685[17] = 0;
}
void h_30(double *state, double *unused, double *out_2936316675218555998) {
   out_2936316675218555998[0] = state[4];
}
void H_30(double *state, double *unused, double *out_6070451421639023597) {
   out_6070451421639023597[0] = 0;
   out_6070451421639023597[1] = 0;
   out_6070451421639023597[2] = 0;
   out_6070451421639023597[3] = 0;
   out_6070451421639023597[4] = 1;
   out_6070451421639023597[5] = 0;
   out_6070451421639023597[6] = 0;
   out_6070451421639023597[7] = 0;
   out_6070451421639023597[8] = 0;
}
void h_26(double *state, double *unused, double *out_6714117934224998478) {
   out_6714117934224998478[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6856644432892575571) {
   out_6856644432892575571[0] = 0;
   out_6856644432892575571[1] = 0;
   out_6856644432892575571[2] = 0;
   out_6856644432892575571[3] = 0;
   out_6856644432892575571[4] = 0;
   out_6856644432892575571[5] = 0;
   out_6856644432892575571[6] = 0;
   out_6856644432892575571[7] = 1;
   out_6856644432892575571[8] = 0;
}
void h_27(double *state, double *unused, double *out_4437834435808272455) {
   out_4437834435808272455[0] = state[3];
}
void H_27(double *state, double *unused, double *out_8294045492822966814) {
   out_8294045492822966814[0] = 0;
   out_8294045492822966814[1] = 0;
   out_8294045492822966814[2] = 0;
   out_8294045492822966814[3] = 1;
   out_8294045492822966814[4] = 0;
   out_8294045492822966814[5] = 0;
   out_8294045492822966814[6] = 0;
   out_8294045492822966814[7] = 0;
   out_8294045492822966814[8] = 0;
}
void h_29(double *state, double *unused, double *out_1986884048044984833) {
   out_1986884048044984833[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6580682765953415781) {
   out_6580682765953415781[0] = 0;
   out_6580682765953415781[1] = 1;
   out_6580682765953415781[2] = 0;
   out_6580682765953415781[3] = 0;
   out_6580682765953415781[4] = 0;
   out_6580682765953415781[5] = 0;
   out_6580682765953415781[6] = 0;
   out_6580682765953415781[7] = 0;
   out_6580682765953415781[8] = 0;
}
void h_28(double *state, double *unused, double *out_2818309281285179254) {
   out_2818309281285179254[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8544313037518742032) {
   out_8544313037518742032[0] = 1;
   out_8544313037518742032[1] = 0;
   out_8544313037518742032[2] = 0;
   out_8544313037518742032[3] = 0;
   out_8544313037518742032[4] = 0;
   out_8544313037518742032[5] = 0;
   out_8544313037518742032[6] = 0;
   out_8544313037518742032[7] = 0;
   out_8544313037518742032[8] = 0;
}
void h_31(double *state, double *unused, double *out_886792560776309977) {
   out_886792560776309977[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7817950360065959393) {
   out_7817950360065959393[0] = 0;
   out_7817950360065959393[1] = 0;
   out_7817950360065959393[2] = 0;
   out_7817950360065959393[3] = 0;
   out_7817950360065959393[4] = 0;
   out_7817950360065959393[5] = 0;
   out_7817950360065959393[6] = 0;
   out_7817950360065959393[7] = 0;
   out_7817950360065959393[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_6506715188500082950) {
  err_fun(nom_x, delta_x, out_6506715188500082950);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7066564298617859979) {
  inv_err_fun(nom_x, true_x, out_7066564298617859979);
}
void car_H_mod_fun(double *state, double *out_7075167101777140118) {
  H_mod_fun(state, out_7075167101777140118);
}
void car_f_fun(double *state, double dt, double *out_6100346516483839845) {
  f_fun(state,  dt, out_6100346516483839845);
}
void car_F_fun(double *state, double dt, double *out_6723015174263675602) {
  F_fun(state,  dt, out_6723015174263675602);
}
void car_h_25(double *state, double *unused, double *out_3834518551131794938) {
  h_25(state, unused, out_3834518551131794938);
}
void car_H_25(double *state, double *unused, double *out_7848596321942919821) {
  H_25(state, unused, out_7848596321942919821);
}
void car_h_24(double *state, double *unused, double *out_5358348446771717581) {
  h_24(state, unused, out_5358348446771717581);
}
void car_H_24(double *state, double *unused, double *out_4290670723140596685) {
  H_24(state, unused, out_4290670723140596685);
}
void car_h_30(double *state, double *unused, double *out_2936316675218555998) {
  h_30(state, unused, out_2936316675218555998);
}
void car_H_30(double *state, double *unused, double *out_6070451421639023597) {
  H_30(state, unused, out_6070451421639023597);
}
void car_h_26(double *state, double *unused, double *out_6714117934224998478) {
  h_26(state, unused, out_6714117934224998478);
}
void car_H_26(double *state, double *unused, double *out_6856644432892575571) {
  H_26(state, unused, out_6856644432892575571);
}
void car_h_27(double *state, double *unused, double *out_4437834435808272455) {
  h_27(state, unused, out_4437834435808272455);
}
void car_H_27(double *state, double *unused, double *out_8294045492822966814) {
  H_27(state, unused, out_8294045492822966814);
}
void car_h_29(double *state, double *unused, double *out_1986884048044984833) {
  h_29(state, unused, out_1986884048044984833);
}
void car_H_29(double *state, double *unused, double *out_6580682765953415781) {
  H_29(state, unused, out_6580682765953415781);
}
void car_h_28(double *state, double *unused, double *out_2818309281285179254) {
  h_28(state, unused, out_2818309281285179254);
}
void car_H_28(double *state, double *unused, double *out_8544313037518742032) {
  H_28(state, unused, out_8544313037518742032);
}
void car_h_31(double *state, double *unused, double *out_886792560776309977) {
  h_31(state, unused, out_886792560776309977);
}
void car_H_31(double *state, double *unused, double *out_7817950360065959393) {
  H_31(state, unused, out_7817950360065959393);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)

#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_390439054689636793) {
   out_390439054689636793[0] = delta_x[0] + nom_x[0];
   out_390439054689636793[1] = delta_x[1] + nom_x[1];
   out_390439054689636793[2] = delta_x[2] + nom_x[2];
   out_390439054689636793[3] = delta_x[3] + nom_x[3];
   out_390439054689636793[4] = delta_x[4] + nom_x[4];
   out_390439054689636793[5] = delta_x[5] + nom_x[5];
   out_390439054689636793[6] = delta_x[6] + nom_x[6];
   out_390439054689636793[7] = delta_x[7] + nom_x[7];
   out_390439054689636793[8] = delta_x[8] + nom_x[8];
   out_390439054689636793[9] = delta_x[9] + nom_x[9];
   out_390439054689636793[10] = delta_x[10] + nom_x[10];
   out_390439054689636793[11] = delta_x[11] + nom_x[11];
   out_390439054689636793[12] = delta_x[12] + nom_x[12];
   out_390439054689636793[13] = delta_x[13] + nom_x[13];
   out_390439054689636793[14] = delta_x[14] + nom_x[14];
   out_390439054689636793[15] = delta_x[15] + nom_x[15];
   out_390439054689636793[16] = delta_x[16] + nom_x[16];
   out_390439054689636793[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7990457038845758323) {
   out_7990457038845758323[0] = -nom_x[0] + true_x[0];
   out_7990457038845758323[1] = -nom_x[1] + true_x[1];
   out_7990457038845758323[2] = -nom_x[2] + true_x[2];
   out_7990457038845758323[3] = -nom_x[3] + true_x[3];
   out_7990457038845758323[4] = -nom_x[4] + true_x[4];
   out_7990457038845758323[5] = -nom_x[5] + true_x[5];
   out_7990457038845758323[6] = -nom_x[6] + true_x[6];
   out_7990457038845758323[7] = -nom_x[7] + true_x[7];
   out_7990457038845758323[8] = -nom_x[8] + true_x[8];
   out_7990457038845758323[9] = -nom_x[9] + true_x[9];
   out_7990457038845758323[10] = -nom_x[10] + true_x[10];
   out_7990457038845758323[11] = -nom_x[11] + true_x[11];
   out_7990457038845758323[12] = -nom_x[12] + true_x[12];
   out_7990457038845758323[13] = -nom_x[13] + true_x[13];
   out_7990457038845758323[14] = -nom_x[14] + true_x[14];
   out_7990457038845758323[15] = -nom_x[15] + true_x[15];
   out_7990457038845758323[16] = -nom_x[16] + true_x[16];
   out_7990457038845758323[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_228771635186623352) {
   out_228771635186623352[0] = 1.0;
   out_228771635186623352[1] = 0.0;
   out_228771635186623352[2] = 0.0;
   out_228771635186623352[3] = 0.0;
   out_228771635186623352[4] = 0.0;
   out_228771635186623352[5] = 0.0;
   out_228771635186623352[6] = 0.0;
   out_228771635186623352[7] = 0.0;
   out_228771635186623352[8] = 0.0;
   out_228771635186623352[9] = 0.0;
   out_228771635186623352[10] = 0.0;
   out_228771635186623352[11] = 0.0;
   out_228771635186623352[12] = 0.0;
   out_228771635186623352[13] = 0.0;
   out_228771635186623352[14] = 0.0;
   out_228771635186623352[15] = 0.0;
   out_228771635186623352[16] = 0.0;
   out_228771635186623352[17] = 0.0;
   out_228771635186623352[18] = 0.0;
   out_228771635186623352[19] = 1.0;
   out_228771635186623352[20] = 0.0;
   out_228771635186623352[21] = 0.0;
   out_228771635186623352[22] = 0.0;
   out_228771635186623352[23] = 0.0;
   out_228771635186623352[24] = 0.0;
   out_228771635186623352[25] = 0.0;
   out_228771635186623352[26] = 0.0;
   out_228771635186623352[27] = 0.0;
   out_228771635186623352[28] = 0.0;
   out_228771635186623352[29] = 0.0;
   out_228771635186623352[30] = 0.0;
   out_228771635186623352[31] = 0.0;
   out_228771635186623352[32] = 0.0;
   out_228771635186623352[33] = 0.0;
   out_228771635186623352[34] = 0.0;
   out_228771635186623352[35] = 0.0;
   out_228771635186623352[36] = 0.0;
   out_228771635186623352[37] = 0.0;
   out_228771635186623352[38] = 1.0;
   out_228771635186623352[39] = 0.0;
   out_228771635186623352[40] = 0.0;
   out_228771635186623352[41] = 0.0;
   out_228771635186623352[42] = 0.0;
   out_228771635186623352[43] = 0.0;
   out_228771635186623352[44] = 0.0;
   out_228771635186623352[45] = 0.0;
   out_228771635186623352[46] = 0.0;
   out_228771635186623352[47] = 0.0;
   out_228771635186623352[48] = 0.0;
   out_228771635186623352[49] = 0.0;
   out_228771635186623352[50] = 0.0;
   out_228771635186623352[51] = 0.0;
   out_228771635186623352[52] = 0.0;
   out_228771635186623352[53] = 0.0;
   out_228771635186623352[54] = 0.0;
   out_228771635186623352[55] = 0.0;
   out_228771635186623352[56] = 0.0;
   out_228771635186623352[57] = 1.0;
   out_228771635186623352[58] = 0.0;
   out_228771635186623352[59] = 0.0;
   out_228771635186623352[60] = 0.0;
   out_228771635186623352[61] = 0.0;
   out_228771635186623352[62] = 0.0;
   out_228771635186623352[63] = 0.0;
   out_228771635186623352[64] = 0.0;
   out_228771635186623352[65] = 0.0;
   out_228771635186623352[66] = 0.0;
   out_228771635186623352[67] = 0.0;
   out_228771635186623352[68] = 0.0;
   out_228771635186623352[69] = 0.0;
   out_228771635186623352[70] = 0.0;
   out_228771635186623352[71] = 0.0;
   out_228771635186623352[72] = 0.0;
   out_228771635186623352[73] = 0.0;
   out_228771635186623352[74] = 0.0;
   out_228771635186623352[75] = 0.0;
   out_228771635186623352[76] = 1.0;
   out_228771635186623352[77] = 0.0;
   out_228771635186623352[78] = 0.0;
   out_228771635186623352[79] = 0.0;
   out_228771635186623352[80] = 0.0;
   out_228771635186623352[81] = 0.0;
   out_228771635186623352[82] = 0.0;
   out_228771635186623352[83] = 0.0;
   out_228771635186623352[84] = 0.0;
   out_228771635186623352[85] = 0.0;
   out_228771635186623352[86] = 0.0;
   out_228771635186623352[87] = 0.0;
   out_228771635186623352[88] = 0.0;
   out_228771635186623352[89] = 0.0;
   out_228771635186623352[90] = 0.0;
   out_228771635186623352[91] = 0.0;
   out_228771635186623352[92] = 0.0;
   out_228771635186623352[93] = 0.0;
   out_228771635186623352[94] = 0.0;
   out_228771635186623352[95] = 1.0;
   out_228771635186623352[96] = 0.0;
   out_228771635186623352[97] = 0.0;
   out_228771635186623352[98] = 0.0;
   out_228771635186623352[99] = 0.0;
   out_228771635186623352[100] = 0.0;
   out_228771635186623352[101] = 0.0;
   out_228771635186623352[102] = 0.0;
   out_228771635186623352[103] = 0.0;
   out_228771635186623352[104] = 0.0;
   out_228771635186623352[105] = 0.0;
   out_228771635186623352[106] = 0.0;
   out_228771635186623352[107] = 0.0;
   out_228771635186623352[108] = 0.0;
   out_228771635186623352[109] = 0.0;
   out_228771635186623352[110] = 0.0;
   out_228771635186623352[111] = 0.0;
   out_228771635186623352[112] = 0.0;
   out_228771635186623352[113] = 0.0;
   out_228771635186623352[114] = 1.0;
   out_228771635186623352[115] = 0.0;
   out_228771635186623352[116] = 0.0;
   out_228771635186623352[117] = 0.0;
   out_228771635186623352[118] = 0.0;
   out_228771635186623352[119] = 0.0;
   out_228771635186623352[120] = 0.0;
   out_228771635186623352[121] = 0.0;
   out_228771635186623352[122] = 0.0;
   out_228771635186623352[123] = 0.0;
   out_228771635186623352[124] = 0.0;
   out_228771635186623352[125] = 0.0;
   out_228771635186623352[126] = 0.0;
   out_228771635186623352[127] = 0.0;
   out_228771635186623352[128] = 0.0;
   out_228771635186623352[129] = 0.0;
   out_228771635186623352[130] = 0.0;
   out_228771635186623352[131] = 0.0;
   out_228771635186623352[132] = 0.0;
   out_228771635186623352[133] = 1.0;
   out_228771635186623352[134] = 0.0;
   out_228771635186623352[135] = 0.0;
   out_228771635186623352[136] = 0.0;
   out_228771635186623352[137] = 0.0;
   out_228771635186623352[138] = 0.0;
   out_228771635186623352[139] = 0.0;
   out_228771635186623352[140] = 0.0;
   out_228771635186623352[141] = 0.0;
   out_228771635186623352[142] = 0.0;
   out_228771635186623352[143] = 0.0;
   out_228771635186623352[144] = 0.0;
   out_228771635186623352[145] = 0.0;
   out_228771635186623352[146] = 0.0;
   out_228771635186623352[147] = 0.0;
   out_228771635186623352[148] = 0.0;
   out_228771635186623352[149] = 0.0;
   out_228771635186623352[150] = 0.0;
   out_228771635186623352[151] = 0.0;
   out_228771635186623352[152] = 1.0;
   out_228771635186623352[153] = 0.0;
   out_228771635186623352[154] = 0.0;
   out_228771635186623352[155] = 0.0;
   out_228771635186623352[156] = 0.0;
   out_228771635186623352[157] = 0.0;
   out_228771635186623352[158] = 0.0;
   out_228771635186623352[159] = 0.0;
   out_228771635186623352[160] = 0.0;
   out_228771635186623352[161] = 0.0;
   out_228771635186623352[162] = 0.0;
   out_228771635186623352[163] = 0.0;
   out_228771635186623352[164] = 0.0;
   out_228771635186623352[165] = 0.0;
   out_228771635186623352[166] = 0.0;
   out_228771635186623352[167] = 0.0;
   out_228771635186623352[168] = 0.0;
   out_228771635186623352[169] = 0.0;
   out_228771635186623352[170] = 0.0;
   out_228771635186623352[171] = 1.0;
   out_228771635186623352[172] = 0.0;
   out_228771635186623352[173] = 0.0;
   out_228771635186623352[174] = 0.0;
   out_228771635186623352[175] = 0.0;
   out_228771635186623352[176] = 0.0;
   out_228771635186623352[177] = 0.0;
   out_228771635186623352[178] = 0.0;
   out_228771635186623352[179] = 0.0;
   out_228771635186623352[180] = 0.0;
   out_228771635186623352[181] = 0.0;
   out_228771635186623352[182] = 0.0;
   out_228771635186623352[183] = 0.0;
   out_228771635186623352[184] = 0.0;
   out_228771635186623352[185] = 0.0;
   out_228771635186623352[186] = 0.0;
   out_228771635186623352[187] = 0.0;
   out_228771635186623352[188] = 0.0;
   out_228771635186623352[189] = 0.0;
   out_228771635186623352[190] = 1.0;
   out_228771635186623352[191] = 0.0;
   out_228771635186623352[192] = 0.0;
   out_228771635186623352[193] = 0.0;
   out_228771635186623352[194] = 0.0;
   out_228771635186623352[195] = 0.0;
   out_228771635186623352[196] = 0.0;
   out_228771635186623352[197] = 0.0;
   out_228771635186623352[198] = 0.0;
   out_228771635186623352[199] = 0.0;
   out_228771635186623352[200] = 0.0;
   out_228771635186623352[201] = 0.0;
   out_228771635186623352[202] = 0.0;
   out_228771635186623352[203] = 0.0;
   out_228771635186623352[204] = 0.0;
   out_228771635186623352[205] = 0.0;
   out_228771635186623352[206] = 0.0;
   out_228771635186623352[207] = 0.0;
   out_228771635186623352[208] = 0.0;
   out_228771635186623352[209] = 1.0;
   out_228771635186623352[210] = 0.0;
   out_228771635186623352[211] = 0.0;
   out_228771635186623352[212] = 0.0;
   out_228771635186623352[213] = 0.0;
   out_228771635186623352[214] = 0.0;
   out_228771635186623352[215] = 0.0;
   out_228771635186623352[216] = 0.0;
   out_228771635186623352[217] = 0.0;
   out_228771635186623352[218] = 0.0;
   out_228771635186623352[219] = 0.0;
   out_228771635186623352[220] = 0.0;
   out_228771635186623352[221] = 0.0;
   out_228771635186623352[222] = 0.0;
   out_228771635186623352[223] = 0.0;
   out_228771635186623352[224] = 0.0;
   out_228771635186623352[225] = 0.0;
   out_228771635186623352[226] = 0.0;
   out_228771635186623352[227] = 0.0;
   out_228771635186623352[228] = 1.0;
   out_228771635186623352[229] = 0.0;
   out_228771635186623352[230] = 0.0;
   out_228771635186623352[231] = 0.0;
   out_228771635186623352[232] = 0.0;
   out_228771635186623352[233] = 0.0;
   out_228771635186623352[234] = 0.0;
   out_228771635186623352[235] = 0.0;
   out_228771635186623352[236] = 0.0;
   out_228771635186623352[237] = 0.0;
   out_228771635186623352[238] = 0.0;
   out_228771635186623352[239] = 0.0;
   out_228771635186623352[240] = 0.0;
   out_228771635186623352[241] = 0.0;
   out_228771635186623352[242] = 0.0;
   out_228771635186623352[243] = 0.0;
   out_228771635186623352[244] = 0.0;
   out_228771635186623352[245] = 0.0;
   out_228771635186623352[246] = 0.0;
   out_228771635186623352[247] = 1.0;
   out_228771635186623352[248] = 0.0;
   out_228771635186623352[249] = 0.0;
   out_228771635186623352[250] = 0.0;
   out_228771635186623352[251] = 0.0;
   out_228771635186623352[252] = 0.0;
   out_228771635186623352[253] = 0.0;
   out_228771635186623352[254] = 0.0;
   out_228771635186623352[255] = 0.0;
   out_228771635186623352[256] = 0.0;
   out_228771635186623352[257] = 0.0;
   out_228771635186623352[258] = 0.0;
   out_228771635186623352[259] = 0.0;
   out_228771635186623352[260] = 0.0;
   out_228771635186623352[261] = 0.0;
   out_228771635186623352[262] = 0.0;
   out_228771635186623352[263] = 0.0;
   out_228771635186623352[264] = 0.0;
   out_228771635186623352[265] = 0.0;
   out_228771635186623352[266] = 1.0;
   out_228771635186623352[267] = 0.0;
   out_228771635186623352[268] = 0.0;
   out_228771635186623352[269] = 0.0;
   out_228771635186623352[270] = 0.0;
   out_228771635186623352[271] = 0.0;
   out_228771635186623352[272] = 0.0;
   out_228771635186623352[273] = 0.0;
   out_228771635186623352[274] = 0.0;
   out_228771635186623352[275] = 0.0;
   out_228771635186623352[276] = 0.0;
   out_228771635186623352[277] = 0.0;
   out_228771635186623352[278] = 0.0;
   out_228771635186623352[279] = 0.0;
   out_228771635186623352[280] = 0.0;
   out_228771635186623352[281] = 0.0;
   out_228771635186623352[282] = 0.0;
   out_228771635186623352[283] = 0.0;
   out_228771635186623352[284] = 0.0;
   out_228771635186623352[285] = 1.0;
   out_228771635186623352[286] = 0.0;
   out_228771635186623352[287] = 0.0;
   out_228771635186623352[288] = 0.0;
   out_228771635186623352[289] = 0.0;
   out_228771635186623352[290] = 0.0;
   out_228771635186623352[291] = 0.0;
   out_228771635186623352[292] = 0.0;
   out_228771635186623352[293] = 0.0;
   out_228771635186623352[294] = 0.0;
   out_228771635186623352[295] = 0.0;
   out_228771635186623352[296] = 0.0;
   out_228771635186623352[297] = 0.0;
   out_228771635186623352[298] = 0.0;
   out_228771635186623352[299] = 0.0;
   out_228771635186623352[300] = 0.0;
   out_228771635186623352[301] = 0.0;
   out_228771635186623352[302] = 0.0;
   out_228771635186623352[303] = 0.0;
   out_228771635186623352[304] = 1.0;
   out_228771635186623352[305] = 0.0;
   out_228771635186623352[306] = 0.0;
   out_228771635186623352[307] = 0.0;
   out_228771635186623352[308] = 0.0;
   out_228771635186623352[309] = 0.0;
   out_228771635186623352[310] = 0.0;
   out_228771635186623352[311] = 0.0;
   out_228771635186623352[312] = 0.0;
   out_228771635186623352[313] = 0.0;
   out_228771635186623352[314] = 0.0;
   out_228771635186623352[315] = 0.0;
   out_228771635186623352[316] = 0.0;
   out_228771635186623352[317] = 0.0;
   out_228771635186623352[318] = 0.0;
   out_228771635186623352[319] = 0.0;
   out_228771635186623352[320] = 0.0;
   out_228771635186623352[321] = 0.0;
   out_228771635186623352[322] = 0.0;
   out_228771635186623352[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_995521470232249249) {
   out_995521470232249249[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_995521470232249249[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_995521470232249249[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_995521470232249249[3] = dt*state[12] + state[3];
   out_995521470232249249[4] = dt*state[13] + state[4];
   out_995521470232249249[5] = dt*state[14] + state[5];
   out_995521470232249249[6] = state[6];
   out_995521470232249249[7] = state[7];
   out_995521470232249249[8] = state[8];
   out_995521470232249249[9] = state[9];
   out_995521470232249249[10] = state[10];
   out_995521470232249249[11] = state[11];
   out_995521470232249249[12] = state[12];
   out_995521470232249249[13] = state[13];
   out_995521470232249249[14] = state[14];
   out_995521470232249249[15] = state[15];
   out_995521470232249249[16] = state[16];
   out_995521470232249249[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8885441589559760893) {
   out_8885441589559760893[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8885441589559760893[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8885441589559760893[2] = 0;
   out_8885441589559760893[3] = 0;
   out_8885441589559760893[4] = 0;
   out_8885441589559760893[5] = 0;
   out_8885441589559760893[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8885441589559760893[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8885441589559760893[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8885441589559760893[9] = 0;
   out_8885441589559760893[10] = 0;
   out_8885441589559760893[11] = 0;
   out_8885441589559760893[12] = 0;
   out_8885441589559760893[13] = 0;
   out_8885441589559760893[14] = 0;
   out_8885441589559760893[15] = 0;
   out_8885441589559760893[16] = 0;
   out_8885441589559760893[17] = 0;
   out_8885441589559760893[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8885441589559760893[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8885441589559760893[20] = 0;
   out_8885441589559760893[21] = 0;
   out_8885441589559760893[22] = 0;
   out_8885441589559760893[23] = 0;
   out_8885441589559760893[24] = 0;
   out_8885441589559760893[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8885441589559760893[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8885441589559760893[27] = 0;
   out_8885441589559760893[28] = 0;
   out_8885441589559760893[29] = 0;
   out_8885441589559760893[30] = 0;
   out_8885441589559760893[31] = 0;
   out_8885441589559760893[32] = 0;
   out_8885441589559760893[33] = 0;
   out_8885441589559760893[34] = 0;
   out_8885441589559760893[35] = 0;
   out_8885441589559760893[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8885441589559760893[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8885441589559760893[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8885441589559760893[39] = 0;
   out_8885441589559760893[40] = 0;
   out_8885441589559760893[41] = 0;
   out_8885441589559760893[42] = 0;
   out_8885441589559760893[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8885441589559760893[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8885441589559760893[45] = 0;
   out_8885441589559760893[46] = 0;
   out_8885441589559760893[47] = 0;
   out_8885441589559760893[48] = 0;
   out_8885441589559760893[49] = 0;
   out_8885441589559760893[50] = 0;
   out_8885441589559760893[51] = 0;
   out_8885441589559760893[52] = 0;
   out_8885441589559760893[53] = 0;
   out_8885441589559760893[54] = 0;
   out_8885441589559760893[55] = 0;
   out_8885441589559760893[56] = 0;
   out_8885441589559760893[57] = 1;
   out_8885441589559760893[58] = 0;
   out_8885441589559760893[59] = 0;
   out_8885441589559760893[60] = 0;
   out_8885441589559760893[61] = 0;
   out_8885441589559760893[62] = 0;
   out_8885441589559760893[63] = 0;
   out_8885441589559760893[64] = 0;
   out_8885441589559760893[65] = 0;
   out_8885441589559760893[66] = dt;
   out_8885441589559760893[67] = 0;
   out_8885441589559760893[68] = 0;
   out_8885441589559760893[69] = 0;
   out_8885441589559760893[70] = 0;
   out_8885441589559760893[71] = 0;
   out_8885441589559760893[72] = 0;
   out_8885441589559760893[73] = 0;
   out_8885441589559760893[74] = 0;
   out_8885441589559760893[75] = 0;
   out_8885441589559760893[76] = 1;
   out_8885441589559760893[77] = 0;
   out_8885441589559760893[78] = 0;
   out_8885441589559760893[79] = 0;
   out_8885441589559760893[80] = 0;
   out_8885441589559760893[81] = 0;
   out_8885441589559760893[82] = 0;
   out_8885441589559760893[83] = 0;
   out_8885441589559760893[84] = 0;
   out_8885441589559760893[85] = dt;
   out_8885441589559760893[86] = 0;
   out_8885441589559760893[87] = 0;
   out_8885441589559760893[88] = 0;
   out_8885441589559760893[89] = 0;
   out_8885441589559760893[90] = 0;
   out_8885441589559760893[91] = 0;
   out_8885441589559760893[92] = 0;
   out_8885441589559760893[93] = 0;
   out_8885441589559760893[94] = 0;
   out_8885441589559760893[95] = 1;
   out_8885441589559760893[96] = 0;
   out_8885441589559760893[97] = 0;
   out_8885441589559760893[98] = 0;
   out_8885441589559760893[99] = 0;
   out_8885441589559760893[100] = 0;
   out_8885441589559760893[101] = 0;
   out_8885441589559760893[102] = 0;
   out_8885441589559760893[103] = 0;
   out_8885441589559760893[104] = dt;
   out_8885441589559760893[105] = 0;
   out_8885441589559760893[106] = 0;
   out_8885441589559760893[107] = 0;
   out_8885441589559760893[108] = 0;
   out_8885441589559760893[109] = 0;
   out_8885441589559760893[110] = 0;
   out_8885441589559760893[111] = 0;
   out_8885441589559760893[112] = 0;
   out_8885441589559760893[113] = 0;
   out_8885441589559760893[114] = 1;
   out_8885441589559760893[115] = 0;
   out_8885441589559760893[116] = 0;
   out_8885441589559760893[117] = 0;
   out_8885441589559760893[118] = 0;
   out_8885441589559760893[119] = 0;
   out_8885441589559760893[120] = 0;
   out_8885441589559760893[121] = 0;
   out_8885441589559760893[122] = 0;
   out_8885441589559760893[123] = 0;
   out_8885441589559760893[124] = 0;
   out_8885441589559760893[125] = 0;
   out_8885441589559760893[126] = 0;
   out_8885441589559760893[127] = 0;
   out_8885441589559760893[128] = 0;
   out_8885441589559760893[129] = 0;
   out_8885441589559760893[130] = 0;
   out_8885441589559760893[131] = 0;
   out_8885441589559760893[132] = 0;
   out_8885441589559760893[133] = 1;
   out_8885441589559760893[134] = 0;
   out_8885441589559760893[135] = 0;
   out_8885441589559760893[136] = 0;
   out_8885441589559760893[137] = 0;
   out_8885441589559760893[138] = 0;
   out_8885441589559760893[139] = 0;
   out_8885441589559760893[140] = 0;
   out_8885441589559760893[141] = 0;
   out_8885441589559760893[142] = 0;
   out_8885441589559760893[143] = 0;
   out_8885441589559760893[144] = 0;
   out_8885441589559760893[145] = 0;
   out_8885441589559760893[146] = 0;
   out_8885441589559760893[147] = 0;
   out_8885441589559760893[148] = 0;
   out_8885441589559760893[149] = 0;
   out_8885441589559760893[150] = 0;
   out_8885441589559760893[151] = 0;
   out_8885441589559760893[152] = 1;
   out_8885441589559760893[153] = 0;
   out_8885441589559760893[154] = 0;
   out_8885441589559760893[155] = 0;
   out_8885441589559760893[156] = 0;
   out_8885441589559760893[157] = 0;
   out_8885441589559760893[158] = 0;
   out_8885441589559760893[159] = 0;
   out_8885441589559760893[160] = 0;
   out_8885441589559760893[161] = 0;
   out_8885441589559760893[162] = 0;
   out_8885441589559760893[163] = 0;
   out_8885441589559760893[164] = 0;
   out_8885441589559760893[165] = 0;
   out_8885441589559760893[166] = 0;
   out_8885441589559760893[167] = 0;
   out_8885441589559760893[168] = 0;
   out_8885441589559760893[169] = 0;
   out_8885441589559760893[170] = 0;
   out_8885441589559760893[171] = 1;
   out_8885441589559760893[172] = 0;
   out_8885441589559760893[173] = 0;
   out_8885441589559760893[174] = 0;
   out_8885441589559760893[175] = 0;
   out_8885441589559760893[176] = 0;
   out_8885441589559760893[177] = 0;
   out_8885441589559760893[178] = 0;
   out_8885441589559760893[179] = 0;
   out_8885441589559760893[180] = 0;
   out_8885441589559760893[181] = 0;
   out_8885441589559760893[182] = 0;
   out_8885441589559760893[183] = 0;
   out_8885441589559760893[184] = 0;
   out_8885441589559760893[185] = 0;
   out_8885441589559760893[186] = 0;
   out_8885441589559760893[187] = 0;
   out_8885441589559760893[188] = 0;
   out_8885441589559760893[189] = 0;
   out_8885441589559760893[190] = 1;
   out_8885441589559760893[191] = 0;
   out_8885441589559760893[192] = 0;
   out_8885441589559760893[193] = 0;
   out_8885441589559760893[194] = 0;
   out_8885441589559760893[195] = 0;
   out_8885441589559760893[196] = 0;
   out_8885441589559760893[197] = 0;
   out_8885441589559760893[198] = 0;
   out_8885441589559760893[199] = 0;
   out_8885441589559760893[200] = 0;
   out_8885441589559760893[201] = 0;
   out_8885441589559760893[202] = 0;
   out_8885441589559760893[203] = 0;
   out_8885441589559760893[204] = 0;
   out_8885441589559760893[205] = 0;
   out_8885441589559760893[206] = 0;
   out_8885441589559760893[207] = 0;
   out_8885441589559760893[208] = 0;
   out_8885441589559760893[209] = 1;
   out_8885441589559760893[210] = 0;
   out_8885441589559760893[211] = 0;
   out_8885441589559760893[212] = 0;
   out_8885441589559760893[213] = 0;
   out_8885441589559760893[214] = 0;
   out_8885441589559760893[215] = 0;
   out_8885441589559760893[216] = 0;
   out_8885441589559760893[217] = 0;
   out_8885441589559760893[218] = 0;
   out_8885441589559760893[219] = 0;
   out_8885441589559760893[220] = 0;
   out_8885441589559760893[221] = 0;
   out_8885441589559760893[222] = 0;
   out_8885441589559760893[223] = 0;
   out_8885441589559760893[224] = 0;
   out_8885441589559760893[225] = 0;
   out_8885441589559760893[226] = 0;
   out_8885441589559760893[227] = 0;
   out_8885441589559760893[228] = 1;
   out_8885441589559760893[229] = 0;
   out_8885441589559760893[230] = 0;
   out_8885441589559760893[231] = 0;
   out_8885441589559760893[232] = 0;
   out_8885441589559760893[233] = 0;
   out_8885441589559760893[234] = 0;
   out_8885441589559760893[235] = 0;
   out_8885441589559760893[236] = 0;
   out_8885441589559760893[237] = 0;
   out_8885441589559760893[238] = 0;
   out_8885441589559760893[239] = 0;
   out_8885441589559760893[240] = 0;
   out_8885441589559760893[241] = 0;
   out_8885441589559760893[242] = 0;
   out_8885441589559760893[243] = 0;
   out_8885441589559760893[244] = 0;
   out_8885441589559760893[245] = 0;
   out_8885441589559760893[246] = 0;
   out_8885441589559760893[247] = 1;
   out_8885441589559760893[248] = 0;
   out_8885441589559760893[249] = 0;
   out_8885441589559760893[250] = 0;
   out_8885441589559760893[251] = 0;
   out_8885441589559760893[252] = 0;
   out_8885441589559760893[253] = 0;
   out_8885441589559760893[254] = 0;
   out_8885441589559760893[255] = 0;
   out_8885441589559760893[256] = 0;
   out_8885441589559760893[257] = 0;
   out_8885441589559760893[258] = 0;
   out_8885441589559760893[259] = 0;
   out_8885441589559760893[260] = 0;
   out_8885441589559760893[261] = 0;
   out_8885441589559760893[262] = 0;
   out_8885441589559760893[263] = 0;
   out_8885441589559760893[264] = 0;
   out_8885441589559760893[265] = 0;
   out_8885441589559760893[266] = 1;
   out_8885441589559760893[267] = 0;
   out_8885441589559760893[268] = 0;
   out_8885441589559760893[269] = 0;
   out_8885441589559760893[270] = 0;
   out_8885441589559760893[271] = 0;
   out_8885441589559760893[272] = 0;
   out_8885441589559760893[273] = 0;
   out_8885441589559760893[274] = 0;
   out_8885441589559760893[275] = 0;
   out_8885441589559760893[276] = 0;
   out_8885441589559760893[277] = 0;
   out_8885441589559760893[278] = 0;
   out_8885441589559760893[279] = 0;
   out_8885441589559760893[280] = 0;
   out_8885441589559760893[281] = 0;
   out_8885441589559760893[282] = 0;
   out_8885441589559760893[283] = 0;
   out_8885441589559760893[284] = 0;
   out_8885441589559760893[285] = 1;
   out_8885441589559760893[286] = 0;
   out_8885441589559760893[287] = 0;
   out_8885441589559760893[288] = 0;
   out_8885441589559760893[289] = 0;
   out_8885441589559760893[290] = 0;
   out_8885441589559760893[291] = 0;
   out_8885441589559760893[292] = 0;
   out_8885441589559760893[293] = 0;
   out_8885441589559760893[294] = 0;
   out_8885441589559760893[295] = 0;
   out_8885441589559760893[296] = 0;
   out_8885441589559760893[297] = 0;
   out_8885441589559760893[298] = 0;
   out_8885441589559760893[299] = 0;
   out_8885441589559760893[300] = 0;
   out_8885441589559760893[301] = 0;
   out_8885441589559760893[302] = 0;
   out_8885441589559760893[303] = 0;
   out_8885441589559760893[304] = 1;
   out_8885441589559760893[305] = 0;
   out_8885441589559760893[306] = 0;
   out_8885441589559760893[307] = 0;
   out_8885441589559760893[308] = 0;
   out_8885441589559760893[309] = 0;
   out_8885441589559760893[310] = 0;
   out_8885441589559760893[311] = 0;
   out_8885441589559760893[312] = 0;
   out_8885441589559760893[313] = 0;
   out_8885441589559760893[314] = 0;
   out_8885441589559760893[315] = 0;
   out_8885441589559760893[316] = 0;
   out_8885441589559760893[317] = 0;
   out_8885441589559760893[318] = 0;
   out_8885441589559760893[319] = 0;
   out_8885441589559760893[320] = 0;
   out_8885441589559760893[321] = 0;
   out_8885441589559760893[322] = 0;
   out_8885441589559760893[323] = 1;
}
void h_4(double *state, double *unused, double *out_7395363253468584448) {
   out_7395363253468584448[0] = state[6] + state[9];
   out_7395363253468584448[1] = state[7] + state[10];
   out_7395363253468584448[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_9173133301244444694) {
   out_9173133301244444694[0] = 0;
   out_9173133301244444694[1] = 0;
   out_9173133301244444694[2] = 0;
   out_9173133301244444694[3] = 0;
   out_9173133301244444694[4] = 0;
   out_9173133301244444694[5] = 0;
   out_9173133301244444694[6] = 1;
   out_9173133301244444694[7] = 0;
   out_9173133301244444694[8] = 0;
   out_9173133301244444694[9] = 1;
   out_9173133301244444694[10] = 0;
   out_9173133301244444694[11] = 0;
   out_9173133301244444694[12] = 0;
   out_9173133301244444694[13] = 0;
   out_9173133301244444694[14] = 0;
   out_9173133301244444694[15] = 0;
   out_9173133301244444694[16] = 0;
   out_9173133301244444694[17] = 0;
   out_9173133301244444694[18] = 0;
   out_9173133301244444694[19] = 0;
   out_9173133301244444694[20] = 0;
   out_9173133301244444694[21] = 0;
   out_9173133301244444694[22] = 0;
   out_9173133301244444694[23] = 0;
   out_9173133301244444694[24] = 0;
   out_9173133301244444694[25] = 1;
   out_9173133301244444694[26] = 0;
   out_9173133301244444694[27] = 0;
   out_9173133301244444694[28] = 1;
   out_9173133301244444694[29] = 0;
   out_9173133301244444694[30] = 0;
   out_9173133301244444694[31] = 0;
   out_9173133301244444694[32] = 0;
   out_9173133301244444694[33] = 0;
   out_9173133301244444694[34] = 0;
   out_9173133301244444694[35] = 0;
   out_9173133301244444694[36] = 0;
   out_9173133301244444694[37] = 0;
   out_9173133301244444694[38] = 0;
   out_9173133301244444694[39] = 0;
   out_9173133301244444694[40] = 0;
   out_9173133301244444694[41] = 0;
   out_9173133301244444694[42] = 0;
   out_9173133301244444694[43] = 0;
   out_9173133301244444694[44] = 1;
   out_9173133301244444694[45] = 0;
   out_9173133301244444694[46] = 0;
   out_9173133301244444694[47] = 1;
   out_9173133301244444694[48] = 0;
   out_9173133301244444694[49] = 0;
   out_9173133301244444694[50] = 0;
   out_9173133301244444694[51] = 0;
   out_9173133301244444694[52] = 0;
   out_9173133301244444694[53] = 0;
}
void h_10(double *state, double *unused, double *out_5791319130957704786) {
   out_5791319130957704786[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5791319130957704786[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5791319130957704786[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_8382500807432592143) {
   out_8382500807432592143[0] = 0;
   out_8382500807432592143[1] = 9.8100000000000005*cos(state[1]);
   out_8382500807432592143[2] = 0;
   out_8382500807432592143[3] = 0;
   out_8382500807432592143[4] = -state[8];
   out_8382500807432592143[5] = state[7];
   out_8382500807432592143[6] = 0;
   out_8382500807432592143[7] = state[5];
   out_8382500807432592143[8] = -state[4];
   out_8382500807432592143[9] = 0;
   out_8382500807432592143[10] = 0;
   out_8382500807432592143[11] = 0;
   out_8382500807432592143[12] = 1;
   out_8382500807432592143[13] = 0;
   out_8382500807432592143[14] = 0;
   out_8382500807432592143[15] = 1;
   out_8382500807432592143[16] = 0;
   out_8382500807432592143[17] = 0;
   out_8382500807432592143[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_8382500807432592143[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_8382500807432592143[20] = 0;
   out_8382500807432592143[21] = state[8];
   out_8382500807432592143[22] = 0;
   out_8382500807432592143[23] = -state[6];
   out_8382500807432592143[24] = -state[5];
   out_8382500807432592143[25] = 0;
   out_8382500807432592143[26] = state[3];
   out_8382500807432592143[27] = 0;
   out_8382500807432592143[28] = 0;
   out_8382500807432592143[29] = 0;
   out_8382500807432592143[30] = 0;
   out_8382500807432592143[31] = 1;
   out_8382500807432592143[32] = 0;
   out_8382500807432592143[33] = 0;
   out_8382500807432592143[34] = 1;
   out_8382500807432592143[35] = 0;
   out_8382500807432592143[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_8382500807432592143[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_8382500807432592143[38] = 0;
   out_8382500807432592143[39] = -state[7];
   out_8382500807432592143[40] = state[6];
   out_8382500807432592143[41] = 0;
   out_8382500807432592143[42] = state[4];
   out_8382500807432592143[43] = -state[3];
   out_8382500807432592143[44] = 0;
   out_8382500807432592143[45] = 0;
   out_8382500807432592143[46] = 0;
   out_8382500807432592143[47] = 0;
   out_8382500807432592143[48] = 0;
   out_8382500807432592143[49] = 0;
   out_8382500807432592143[50] = 1;
   out_8382500807432592143[51] = 0;
   out_8382500807432592143[52] = 0;
   out_8382500807432592143[53] = 1;
}
void h_13(double *state, double *unused, double *out_8786519752124647312) {
   out_8786519752124647312[0] = state[3];
   out_8786519752124647312[1] = state[4];
   out_8786519752124647312[2] = state[5];
}
void H_13(double *state, double *unused, double *out_5960859475912111893) {
   out_5960859475912111893[0] = 0;
   out_5960859475912111893[1] = 0;
   out_5960859475912111893[2] = 0;
   out_5960859475912111893[3] = 1;
   out_5960859475912111893[4] = 0;
   out_5960859475912111893[5] = 0;
   out_5960859475912111893[6] = 0;
   out_5960859475912111893[7] = 0;
   out_5960859475912111893[8] = 0;
   out_5960859475912111893[9] = 0;
   out_5960859475912111893[10] = 0;
   out_5960859475912111893[11] = 0;
   out_5960859475912111893[12] = 0;
   out_5960859475912111893[13] = 0;
   out_5960859475912111893[14] = 0;
   out_5960859475912111893[15] = 0;
   out_5960859475912111893[16] = 0;
   out_5960859475912111893[17] = 0;
   out_5960859475912111893[18] = 0;
   out_5960859475912111893[19] = 0;
   out_5960859475912111893[20] = 0;
   out_5960859475912111893[21] = 0;
   out_5960859475912111893[22] = 1;
   out_5960859475912111893[23] = 0;
   out_5960859475912111893[24] = 0;
   out_5960859475912111893[25] = 0;
   out_5960859475912111893[26] = 0;
   out_5960859475912111893[27] = 0;
   out_5960859475912111893[28] = 0;
   out_5960859475912111893[29] = 0;
   out_5960859475912111893[30] = 0;
   out_5960859475912111893[31] = 0;
   out_5960859475912111893[32] = 0;
   out_5960859475912111893[33] = 0;
   out_5960859475912111893[34] = 0;
   out_5960859475912111893[35] = 0;
   out_5960859475912111893[36] = 0;
   out_5960859475912111893[37] = 0;
   out_5960859475912111893[38] = 0;
   out_5960859475912111893[39] = 0;
   out_5960859475912111893[40] = 0;
   out_5960859475912111893[41] = 1;
   out_5960859475912111893[42] = 0;
   out_5960859475912111893[43] = 0;
   out_5960859475912111893[44] = 0;
   out_5960859475912111893[45] = 0;
   out_5960859475912111893[46] = 0;
   out_5960859475912111893[47] = 0;
   out_5960859475912111893[48] = 0;
   out_5960859475912111893[49] = 0;
   out_5960859475912111893[50] = 0;
   out_5960859475912111893[51] = 0;
   out_5960859475912111893[52] = 0;
   out_5960859475912111893[53] = 0;
}
void h_14(double *state, double *unused, double *out_7337444961737170917) {
   out_7337444961737170917[0] = state[6];
   out_7337444961737170917[1] = state[7];
   out_7337444961737170917[2] = state[8];
}
void H_14(double *state, double *unused, double *out_1792464957185366498) {
   out_1792464957185366498[0] = 0;
   out_1792464957185366498[1] = 0;
   out_1792464957185366498[2] = 0;
   out_1792464957185366498[3] = 0;
   out_1792464957185366498[4] = 0;
   out_1792464957185366498[5] = 0;
   out_1792464957185366498[6] = 1;
   out_1792464957185366498[7] = 0;
   out_1792464957185366498[8] = 0;
   out_1792464957185366498[9] = 0;
   out_1792464957185366498[10] = 0;
   out_1792464957185366498[11] = 0;
   out_1792464957185366498[12] = 0;
   out_1792464957185366498[13] = 0;
   out_1792464957185366498[14] = 0;
   out_1792464957185366498[15] = 0;
   out_1792464957185366498[16] = 0;
   out_1792464957185366498[17] = 0;
   out_1792464957185366498[18] = 0;
   out_1792464957185366498[19] = 0;
   out_1792464957185366498[20] = 0;
   out_1792464957185366498[21] = 0;
   out_1792464957185366498[22] = 0;
   out_1792464957185366498[23] = 0;
   out_1792464957185366498[24] = 0;
   out_1792464957185366498[25] = 1;
   out_1792464957185366498[26] = 0;
   out_1792464957185366498[27] = 0;
   out_1792464957185366498[28] = 0;
   out_1792464957185366498[29] = 0;
   out_1792464957185366498[30] = 0;
   out_1792464957185366498[31] = 0;
   out_1792464957185366498[32] = 0;
   out_1792464957185366498[33] = 0;
   out_1792464957185366498[34] = 0;
   out_1792464957185366498[35] = 0;
   out_1792464957185366498[36] = 0;
   out_1792464957185366498[37] = 0;
   out_1792464957185366498[38] = 0;
   out_1792464957185366498[39] = 0;
   out_1792464957185366498[40] = 0;
   out_1792464957185366498[41] = 0;
   out_1792464957185366498[42] = 0;
   out_1792464957185366498[43] = 0;
   out_1792464957185366498[44] = 1;
   out_1792464957185366498[45] = 0;
   out_1792464957185366498[46] = 0;
   out_1792464957185366498[47] = 0;
   out_1792464957185366498[48] = 0;
   out_1792464957185366498[49] = 0;
   out_1792464957185366498[50] = 0;
   out_1792464957185366498[51] = 0;
   out_1792464957185366498[52] = 0;
   out_1792464957185366498[53] = 0;
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

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_390439054689636793) {
  err_fun(nom_x, delta_x, out_390439054689636793);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7990457038845758323) {
  inv_err_fun(nom_x, true_x, out_7990457038845758323);
}
void pose_H_mod_fun(double *state, double *out_228771635186623352) {
  H_mod_fun(state, out_228771635186623352);
}
void pose_f_fun(double *state, double dt, double *out_995521470232249249) {
  f_fun(state,  dt, out_995521470232249249);
}
void pose_F_fun(double *state, double dt, double *out_8885441589559760893) {
  F_fun(state,  dt, out_8885441589559760893);
}
void pose_h_4(double *state, double *unused, double *out_7395363253468584448) {
  h_4(state, unused, out_7395363253468584448);
}
void pose_H_4(double *state, double *unused, double *out_9173133301244444694) {
  H_4(state, unused, out_9173133301244444694);
}
void pose_h_10(double *state, double *unused, double *out_5791319130957704786) {
  h_10(state, unused, out_5791319130957704786);
}
void pose_H_10(double *state, double *unused, double *out_8382500807432592143) {
  H_10(state, unused, out_8382500807432592143);
}
void pose_h_13(double *state, double *unused, double *out_8786519752124647312) {
  h_13(state, unused, out_8786519752124647312);
}
void pose_H_13(double *state, double *unused, double *out_5960859475912111893) {
  H_13(state, unused, out_5960859475912111893);
}
void pose_h_14(double *state, double *unused, double *out_7337444961737170917) {
  h_14(state, unused, out_7337444961737170917);
}
void pose_H_14(double *state, double *unused, double *out_1792464957185366498) {
  H_14(state, unused, out_1792464957185366498);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)

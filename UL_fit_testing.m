h0 = Strain(1:8);
r100 = Ratio100(49:56);
r150 = Ratio150(49:56);
r200 = Ratio200(49:56);
r250 = Ratio250(49:56);

uls = [];
cis = [];

logistic = @(x,xdata)(1./(1+exp(-x(1).*(xdata-x(2)))));

[a,b,beta] = logistic_UL_fit(Strain(1:8),Ratio100(1:8));

uls = [uls a];
cis = [cis b];

hsmooth = (1:400)/1000 + 0.8;

% [a,b] = logistic_UL_fit(Strain2(9:16),Ratios2(9:16));
% 
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(17:24),Ratio100(17:24));
% 
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(25:32),Ratios2(25:32));
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(33:40),Ratios2(33:40));
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(41:48),Ratios2(41:48));
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(49:56),Ratios2(49:56));
% 
% uls = [uls a];
% cis = [cis b];
% 
% [a,b] = logistic_UL_fit(Strain2(49:56),Ratios2(57:64));
% 
% uls = [uls a];
% cis = [cis b];
% 
% uls = transpose(uls);
% cis = transpose(cis);
% 
% freqs = [200;201;202;203;204;205;206;207];
% 
% % delta = beta;
% 
% % 
% % A = [1 1];
% % 
% 
% test = [17  19 21 23]
% 
% h0 = Strain(17:24);
% r100 = Ratio100(17:24);
% 
% logistic = @(x,xdata)(1./(1+exp(-x(1).*(xdata-x(2)))));
% inv_logistic = @(x,UL)(-log(1/UL -1)/x(1) + x(2));
% 
% [beta, R, J, CovB, MSE] = nlinfit(h0,r100,logistic,A);
% ci1 = tinv(0.95,6)*sqrt(sum(R.^2)/6*CovB(1,1))
% ci2 = tinv(0.95,6)*sqrt(sum(R.^2)/6*CovB(2,2))
% hsmooth = [1:400]/1000 + 0.8;
% 
% B = [1];
% 
% logistic1U = @(x,xdata)(1./(1+exp(-(beta(1)+ci1).*(xdata-x))));
% logistic1L = @(x,xdata)(1./(1+exp(-(beta(1)-ci1).*(xdata-x))));
% logistic2U = @(x,xdata)(1./(1+exp(-x.*(xdata-(beta(2)+ci2)))));
% logistic2L = @(x,xdata)(1./(1+exp(-x.*(xdata-(beta(2)-ci2)))));
% 
% [a1, r1, j1, covb1,mse1] = nlinfit(h0,r100,logistic1U,B);
% [a2, r2, j2, covb2,mse2] = nlinfit(h0,r100,logistic1L,B);
% 
% [a3, r3, j3, covb3,mse3] = nlinfit(h0,r100,logistic2U,B);
% [a4, r4, j4, covb4,mse4] = nlinfit(h0,r100,logistic2L,B);
% 
% 
% inv_logistic = @(x,UL)(-log(1/UL -1)/x(1) + x(2));
% 
% invnom = inv_logistic(beta,.95)
% inv1 = inv_logistic([beta(1)+ci1,a1],.95)
% inv2 = inv_logistic([beta(1)-ci1,a2],.95)
% inv3 = inv_logistic([a3,beta(2)+ci2],.95)
% inv4 = inv_logistic([a4,beta(2)-ci2],.95)
% 
% quadsum = sqrt((invnom-inv1)^2 + (invnom-inv2)^2 + (invnom-inv3)^2 + (invnom-inv4)^2)
% 
% tests = [100,150,200,250];
% ULs = [0.9902, 0.9813, 0.9892, 0.9916];
% qsums = [0.0057,0.0049, 0.0039,0.0019];
% 

figure(1)
hold on
plot(h0,r100,'+');
plot(hsmooth,logistic(beta,hsmooth));
plot(invnom, 0.95,'o', invnom-quadsum, 0.95, 'ro', invnom+quadsum,0.95,'ro');
hold off
% 
% % figure(2)
% % errorbar(tests,ULs,qsums,'o')
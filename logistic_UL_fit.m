function [ul, confinterval,beta] = logistic_UL_fit(h0,ratios)

    %define logistic distribution

    logistic = @(x,xdata)(1./(1+exp(-x(1).*(xdata-x(2)))));

    %define inverse logistic function

    inv_logistic = @(x,UL)(-log(1/UL -1)/x(1) + x(2));

    %define dummy fitting parameters

    A = [1,1];
    B = [1];

    %determine best logistic fit to data

    [beta, R, J, CovB, MSE] = nlinfit(h0,ratios,logistic,A);

    %calculate confidence intervals for parameter 1 (rate) and parameter 2
    %(position)

    ci1 = tinv(0.99,6)*sqrt(sum(R.^2)/6*CovB(1,1));
    ci2 = tinv(0.99,6)*sqrt(sum(R.^2)/6*CovB(2,2));

    %define logistic distributions used for determining confidence intervals

    logistic1U = @(x,xdata)(1./(1+exp(-(beta(1)+ci1).*(xdata-x))));
    logistic1L = @(x,xdata)(1./(1+exp(-(beta(1)-ci1).*(xdata-x))));
    logistic2U = @(x,xdata)(1./(1+exp(-x.*(xdata-(beta(2)+ci2)))));
    logistic2L = @(x,xdata)(1./(1+exp(-x.*(xdata-(beta(2)-ci2)))));

    %determine best fit for extrema of confidence intervals

    [a1, r1, j1, covb1,mse1] = nlinfit(h0,ratios,logistic1U,B);
    [a2, r2, j2, covb2,mse2] = nlinfit(h0,ratios,logistic1L,B);
    [a3, r3, j3, covb3,mse3] = nlinfit(h0,ratios,logistic2U,B);
    [a4, r4, j4, covb4,mse4] = nlinfit(h0,ratios,logistic2L,B);

    %use inverse logistic function to determine location of 95% upper limit

    ul = inv_logistic(beta,.95);
    inv1 = inv_logistic([beta(1)+ci1,a1],.95);
    inv2 = inv_logistic([beta(1)-ci1,a2],.95);
    inv3 = inv_logistic([a3,beta(2)+ci2],.95);
    inv4 = inv_logistic([a4,beta(2)-ci2],.95);

    %calculate confidence interval by taking the quadrature sum of the 95% ULs
    %(from nominal)

    confinterval = sqrt((ul-inv1)^2 + (ul-inv2)^2 + (ul-inv3)^2 + (ul-inv4)^2);

end





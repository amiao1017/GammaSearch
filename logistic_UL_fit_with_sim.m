function [nom_ul, uls_mean, uls_std] = logistic_UL_fit_with_sim(h0,ratios)

    %define logistic distribution

    logistic = @(x,xdata)(1./(1+exp(-x(1).*(xdata-x(2)))));

    %define inverse logistic function

    inv_logistic = @(x,UL)(-log(1/UL -1)/x(1) + x(2));

    %define dummy fitting parameters

    A = [1,1];

    %determine best logistic fit to data

    [beta, R, J, CovB, MSE] = nlinfit(h0,ratios,logistic,A);
    
    nom_ul = inv_logistic(beta,.95);

    uls = [];
    confs = [];
    
    for i = 1:1000
        perc = generate_fake_Fstat_trials(beta(1), beta(2), h0,100);
        [ul, conf] = logistic_UL_fit(h0,perc);
        uls = [uls ; ul];
        confs = [confs ; conf];
    end

    for i = 1:length(uls)
        if uls(i) <0
            uls(i) = 0
        end
    end


    uls_mean = mean(uls);
    uls_std = std(uls);
    
end





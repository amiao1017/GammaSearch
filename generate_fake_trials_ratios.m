
function [perc,expectation] = generate_fake_trials_ratios(h0,ratios, ntrials)

logistic = @(a,b,xdata)(1./(1+exp(-a.*(xdata-b))));

n_successes = zeros(length(h0),1);
p_success = ratios;
for i = 1:length(h0)
    for j = 1:ntrials
            trial = rand;
            if (trial <= p_success(i))
                n_successes(i) = n_successes(i) + 1;
            end
end

expectation = ntrials*p_success;
perc = n_successes./ntrials;
 
end
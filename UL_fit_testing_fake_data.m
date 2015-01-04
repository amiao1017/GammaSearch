delta = [6.6115    0.4596];
h0 = Strain(1:8);
uls = [];
confs = [];
uls2 = [];
confs2 = [];
uls3 = [];
confs3 = [];
uls4 = [];
confs4 = [];
delta2 = [5.1488    0.3696];

inv_logistic = @(x,UL)(-log(1/UL -1)/x(1) + x(2));
nom_ul = inv_logistic(delta2,.95);

for i = 1:10000

    perc = generate_fake_Fstat_trials(delta2(1), delta2(2), h0,100);
    perc2 = generate_fake_Fstat_trials(delta2(1), delta2(2), h0,150);
    perc3 = generate_fake_Fstat_trials(delta2(1), delta2(2), h0,200);
    perc4 = generate_fake_Fstat_trials(delta2(1), delta2(2), h0,250);
    [ul, conf] = logistic_UL_fit(h0,perc);
    [ul2, conf2] = logistic_UL_fit(h0,perc2);
    [ul3, conf3] = logistic_UL_fit(h0,perc3);
    [ul4, conf4] = logistic_UL_fit(h0,perc4);
    uls = [uls ; ul];
    confs = [confs ; conf];
    uls2 = [uls2 ; ul2];
    confs2 = [confs2 ; conf2];
    uls3 = [uls3 ; ul3];
    confs3 = [confs3 ; conf3];
    uls4 = [uls4 ; ul4];
    confs4 = [confs4 ; conf4];
    
    
end

for i = 1:length(uls)
if uls(i) <0
uls(i) = 0
end
end

for i = 1:length(uls)
if uls2(i) <0
uls2(i) = 0
end
end

for i = 1:length(uls)
if uls3(i) <0
uls3(i) = 0
end
end

for i = 1:length(uls)
if uls4(i) <0
uls4(i) = 0
end
end

uls_mean = mean(uls);
uls2_mean = mean(uls2);
uls3_mean = mean(uls3);
uls4_mean = mean(uls4);

uls_std = std(uls);
uls2_std = std(uls2);
uls3_std = std(uls3);
uls4_std = std(uls4);

x = [0.5:0.01:1.5];
norm1 = normpdf(x,uls_mean,uls_std);
norm2 = normpdf(x,uls2_mean,uls2_std);
norm3 = normpdf(x,uls3_mean,uls3_std);
norm4 = normpdf(x,uls4_mean,uls4_std);
plot(x,norm1,x,norm2,x,norm3,x,norm4);
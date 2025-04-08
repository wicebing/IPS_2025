library("writexl")
library(openxlsx)
library(readxl)
library(mgcv)
library(oddsratio)
library('vcd')
library(postHoc)

library(foreign)
library(ggplot2)
library(MASS)
require(boot)


indoorPosition <- read.csv("C:/Users/USER/Downloads/IPS/areaPct_exp2_60mins.csv")
data_all <- indoorPosition

data_all$deadzone <- with(data_all, 100*(1- cover_area_pct))

#data_all$ev <- with(data_all, event==2 | event==1)
#data_all_c <- subset(data_all , event==0 | event==1)
#data_all_f <- subset(data_all , event==0 | event==2)
data_all <- within(data_all, {
  event_c <- as.factor(event_c)
})

data_all <- within(data_all, {
  event_f <- as.factor(event_f)
})

data_all <- within(data_all, {
  hour <- as.factor(hour)
})
data_all <- within(data_all, {
  weekday <- as.factor(weekday)
})

data_pre = subset(data_all , id_mins < as.POSIXct("2024-11-17 00:00:00", tz = "Asia/Taipei")) 
data_post = subset(data_all , id_mins >= as.POSIXct("2024-11-17 00:00:00", tz = "Asia/Taipei"))


t.test(deadzone~event_f, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)

# help me to do t.test on areaPct_exp{a}_{b}mins.csv a in [1,2,3]; b in [15,30,45,60,75,90,120]
# this is a sensitivity analysis to see if the areaPct_exp{a}_{b}mins.csv is sensitive to the t.test result
# for example, if a=1 and b=15, then the file name is areaPct_exp1_15mins.csv
# if a=1 and b=30, then the file name is areaPct_exp1_30mins.csv
# if a=2 and b=15, then the file name is areaPct_exp2_15mins.csv
# if a=2 and b=30, then the file name is areaPct_exp2_30mins.csv
# if a=3 and b=15, then the file name is areaPct_exp3_15mins.csv
# if a=3 and b=30, then the file name is areaPct_exp3_30mins.csv
# get all results and save to a csv file
# the file name is areaPct_exp{a}_{b}mins_t_test.csv
# and finally show all result in a table
# the table should include a, b, t.test result, p.value, and confidence interval
# the table should be saved to a csv file


# get all combinations of a and b
# a in [1,2,3]; b in [15,30,45,60,75,90,120]
a <- c(1,2,3,4)
b <- c(15,30,45,60,75,90)
# create a data frame to store the results
# the data frame should include a, b, t.test result, p.value, and confidence interval
# the data frame should be saved to a csv file
results <- data.frame(a=integer(), b=integer(), t.test_result=numeric(), p.value=numeric(), conf.int.lower=numeric(), conf.int.upper=numeric())
# loop through all combinations of a and b
for (i in 1:length(a)) {
  for (j in 1:length(b)) {
    # read the csv file
    file_name <- paste0("C:/Users/USER/Downloads/IPS/areaPct_exp", a[i], "_", b[j], "mins.csv")
    data_all <- read.csv(file_name)
    data_all$deadzone <- with(data_all, 100*(1- cover_area_pct))
    data_all <- within(data_all, {
      event_f <- as.factor(event_f)
    })
    # do t.test on deadzone~event_f
    t.test_result <- t.test(deadzone~event_f, alternative='two.sided', conf.level=.95, 
                             var.equal=TRUE, data=data_all)
    # get the p.value and confidence interval
    p.value <- t.test_result$p.value
    conf.int <- t.test_result$conf.int
    # save the results to the data frame
    results <- rbind(results, data.frame(a=a[i], b=b[j], t.test_result=t.test_result$statistic, p.value=p.value, conf.int.lower=conf.int[1], conf.int.upper=conf.int[2]))
  }
}
# save the results to a csv file 
write.csv(results, "C:/Users/USER/Downloads/IPS/areaPct_exp_t_test_results.csv", row.names=FALSE)



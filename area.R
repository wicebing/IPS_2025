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


indoorPosition <- read.csv("C:/Users/USER/Downloads/IPS/areaPct_exp2_90mins.csv")
data_all <- indoorPosition

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

t.test(cover_area_pct~event_c, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)
t.test(cover_area_pct~event_f, alternative='two.sided', conf.level=.95, 
       var.equal=FALSE, data=data_all)

GLM.2 <- glm(event_f ~ cover_area_pct + hour + weekday, 
             family=binomial(logit), data=data_all)
summary(GLM.2)
exp(coef(GLM.2))  # Exponentiated coefficients ("odds ratios")

GLM.3 <- glm(event_c ~ cover_area_pct + hour + weekday, 
             family=binomial(logit), data=data_all)
summary(GLM.3)
exp(coef(GLM.3))  # Exponentiated coefficients ("odds ratios") 看分布面積對事件的影響

GLM.4 <- glm(cover_area_pct ~ event_c + hour + weekday, 
             family=binomial(logit), data=data_all)
summary(GLM.4)
exp(coef(GLM.4))  # Exponentiated coefficients ("odds ratios") 看事件對分布面積的影響

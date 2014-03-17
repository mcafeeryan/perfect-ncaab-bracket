require(ggplot2)
require(cvTools)
require(pls)

crossval <- function(formula, data, y, train.fn, k){
    segs <- cvsegments(nrow(data), k)
    classrate = c()
    for(seg in segs){
        traindata <- subset(data,!(1:nrow(data) %in% seg))
        fnfit <- train.fn(formula, data= traindata)
        nd <-  subset(data, 1:nrow(data) %in% seg)
        classrate = c(classrate, sum(nd[,y] == predict(fnfit, newdata = nd)))
    }
    return(classrate)
}

all <- read.csv('../training_set/training_data.csv')
all$outcome <- as.factor(all$scorediff > 0)
all$windummy <- all$Wins > 0
teamstats <- read.csv('../training_set/team_stats.csv', sep = '\t')

# Basic Plotting
attach(all)
qplot(all$Points.Per.Game, all$scoreratio) + geom_smooth(method = lm)
ggplot(all, aes(Efficiency, True.Shooting.Pct, colour = (scorediff > 0 ))) + geom_point()
ggplot(all, aes(Efficiency, Wins, colour = (scorediff > 0 ))) + geom_point() + geom_smooth(method = lm)
ggplot(all, aes(X3.pt.Field.Goal.Point.Pct, Offensive.Reb.Pct, colour = (scorediff > 0 ))) + geom_point() + geom_smooth(method = lm)

## fit <- lm(scoreratio ~ Wins + Points.Per.Possessions + True.Shooting.Pct + Rebound.Pct + Assist.to.Turnover)
## fit <- glm(outcome ~ Wins + Points.Per.Possessions + True.Shooting.Pct + Rebound.Pct + Assist.to.Turnover, family = 'binomial', data = all)


# ----- Categorize teams -----
require(mclust)
teamstats <- read.csv('../training_set/team_stats.csv', sep = '\t')
row.names(teamstats) <- paste(teamstats$Team.Name, teamstats$ID)
## clust <- Mclust(data.frame(teamstats$Possessions.Per.40.minutes,
##                            teamstats$Free.Throw.Rate,
##                            teamstats$X3.pt.Field.Goal.Point.Pct,
##                            teamstats$Offensive.Reb.Pct,
##                            teamstats$Assist.to.Turnover,
##                            teamstats$Steal.Pct,
##                            teamstats$True.Shooting.Pct))
require(pvclust)
## clust <- pvclust(data.frame(teamstats$Possessions.Per.40.minutes,
##                            teamstats$Free.Throw.Rate,
##                            teamstats$X3.pt.Field.Goal.Point.Pct,
##                            teamstats$Offensive.Reb.Pct,
##                            teamstats$Assist.to.Turnover,
##                            teamstats$Steal.Pct,
##                            teamstats$True.Shooting.Pct), method.hclust = 'ward', method.dist='euclidean')

teamstats.cluststats <- subset(teamstats, select = c('Steal.Pct', 'Block.Pct', 'Turnover.Pct', 'Defensive.Reb.Pct', 'DefEff'))

# Paint, out, fast and slow categiorizations (pretty decent)
teamstats.cluststats <- subset(teamstats, select = c('Offensive.Reb.Pct', 'Steal.Pct', 'X3.pt.Field.Goal.Point.Pct', 'Turnover.Pct', 'Free.Throw.Rate', 'ESC'))

# Skill, Power, Athleticism categorizations
#teamstats.cluststats <- subset(teamstats, select = c('Offensive.Reb.Pct', 'X3.pt.Field.Goal.Point.Pct','Assist.to.Turnover', 'Free.Throw.Rate'))
teamstats.cluststats <- subset(teamstats, select = c('Offensive.Reb.Pct', 'X3.pt.Field.Goal.Point.Pct','Assist.to.Turnover', 'Free.Throw.Rate', 'Fouls.Per.Game','Assists.Per.Game'))

require(GGally)
require(snow)
#cl <- makeCluster(6)
clust <- Mclust(teamstats.cluststats)
#clust <- pvclust(cl, data = t(teamstats.cluststats), method.hclust = 'ward', method.dist='euclidean')
nclust = 3
clust <- kmeans(teamstats.cluststats, nclust, iter.max = 100)
#ggplot(teamstats, aes(Free.Throw.Rate, X3.pt.Field.Goal.Point.Pct, color = rainbow(nclust)[clust$cluster])) + geom_point()
#ggplot(teamstats, aes(DefEff, OffEff, color = rainbow(nclust)[clust$cluster])) + geom_point()
teamstats.cluststats$clust <-as.factor(clust$cluster)
ggpairs(teamstats.cluststats, color = 'clust', alpha = 0.4)

# Testing different win weights
fit <- glm(outcome ~ Away.Wins + Home.Wins + Neutral.Wins + Possessions.Per.40.minutes + Points, family = 'binomial')
ggplot(all, aes(Away.Wins, Home.Wins, color = outcome)) + geom_point()
summary((predict(fit) > 0) == (outcome))
fit <- lm(scoreratio ~ Away.Wins + Home.Wins + Neutral.Wins)
summary((predict(fit) > 0) == (outcome))
fit <- glm(outcome ~ Away.Wins + Home.Wins + Neutral.Wins + Offensive.Reb.Pct*Possessions + Points.Per.Game + Free.Throw.Rate + X3.pt.Field.Goal.Point.Pct + Assist.to.Turnover*Possessions + True.Shooting.Pct, family = 'binomial')
summary((predict(fit) > 0.5) == (outcome))
fit <- glm(outcome ~ Away.Wins + Home.Wins + Neutral.Wins + Offensive.Reb.Pct + Possessions + Points.Per.Possessions + Free.Throw.Rate + X3.pt.Field.Goal.Point.Pct + Assist.to.Turnover + True.Shooting.Pct, family = 'binomial')
summary((predict(fit) > 0.5) == (outcome))

fit <- glm(outcome ~ Away.Wins + Home.Wins + Neutral.Wins + Points.Per.Possessions + Rebound.Pct + Points.Per.Possessions.Opp, family = 'binomial')
summary((predict(fit) > 0.5) == (as.factor(outcome)))
summary(fit)
fit <- glm(outcome ~ Free.Throw.Rate + Points.Per.Possessions + Rebound.Pct + Assist.Pct + Turnover.Pct + Points.Per.Possessions.Opp + Home.Wins + Neutral.Wins + log(away_wscore) + log(home_wscore))

fit <- glm(outcome ~ Offensive.Reb.Pct + Turnover.Pct +  DefEff + SOS + Wins + OffEff, data = all)
summary((predict(fit) > 0.5) == (outcome))
summary(fit)

# ---- SVM -----
require(e1071)
all$outcome <- as.factor(all$outcome)
outcome <- as.factor(outcome)
fm <- Offensive.Reb.Pct + Turnover.Pct +  DefEff + SOS + Wins + OffEff
fit <- svm(outcome ~ Offensive.Reb.Pct + Turnover.Pct +  DefEff + SOS + Wins + OffEff, cross = 10)
summary(predict(fit) == (as.factor(outcome)))

# CLusters 
prop.table(table(class_matchup, outcome), 1)

home_wscore[home_wscore == 0] <- mean(home_wscore[home_wscore != 0])

fit <- svm(outcome ~ uwevcent + Offensive.Reb.Pct + Turnover.Pct +  DefEff +  OffEff + SOS+ Wins+ ESC + as.factor(class_matchup %in% c(23, 13)), cross = 20, kernel = 'linear')
summary(fit)
summary((predict(fit)) == outcome)

# ---- RandomForest ---- (Bad results)
require(randomForest)
all[is.na(all)] <- 0
train <- data.frame(Offensive.Reb.Pct , Turnover.Pct ,  DefEff ,  OffEff , SOS, Wins , ESC , as.factor(class_matchup %in% c(23, 13)))

rf <- rfcv(train,outcome, 10)

class_matchup <- as.factor(class_matchup)
pvp <- class_matchup == '33'
ava <- class_matchup == '22'
fm <-outcome ~ Pace.Forcing + prev_matches + foulrate.2.FTR + foulrate.2.FTPct + X3.pt.Weakness.Pct + TO.2.Steal + DefReb.2.OffReb+ scwtevcent + locwtevcent +uwevcent  +Turnover.Pct +SOS+  DefEff + Wins + as.factor(class_matchup %in% c(23, 13))
fit <- glm(outcome ~SOS + Wins +uwevcent , family = 'binomial')
fit <- svm(fm, cross = 100, kernel = 'linear')

# Best Model So far
fit <- svm(outcome ~ SOS+ Wins + revevcent + uwevcent + scwtevcent + prev_matches, cross = 100, kernel = 'linear')

ggplot(all, aes(SOS, Wins, color = as.factor(outcome))) + geom_point() + geom_smooth()
fit <- glm(fm, family = 'binomial')
summary(fit)

summary((predict(fit) > 0.5) == outcome)

require(rpart)
tree <- rpart(fm)
summary((predict(tree) > 0.5) == outcome)

# Boosting
booststats <- data.frame(SOS,TO.2.Steal,foulrate.2.FTR,Pace.Forcing,X3.pt.Weakness.Pct, Home.Wins, Wins , revevcent ,locwtevcent, uwevcent , scwtevcent, as.factor(class_matchup %in% c(23, 13)), as.factor(class_matchup %in% c(32, 31)), prev_matches)

k = 20
segs <- cvsegments(nrow(all), k)
classrate = c()

for(seg in segs){
    trainbooststats <- subset(booststats,!(1:nrow(booststats) %in% seg))
    testbooststats <- subset(booststats,(1:nrow(booststats) %in% seg))

    trainoutcome <- outcome[-seg]
    testoutcome <- outcome[seg]
    
    adafit <- ada(trainbooststats, trainoutcome, testbooststats, testoutcome, type = 'gentle')
    classrate <- c(classrate, sum(adafit$fit == adafit$actual)/length(adafit$actual))

}


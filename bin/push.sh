source conf/env.sh
path=${1}

git --git-dir=$path/.git --work-tree=$path status
git --git-dir=$path/.git --work-tree=$path add pomodoro.csv
git --git-dir=$path/.git --work-tree=$path commit --allow-empty-message -m ''
git --git-dir=$path/.git --work-tree=$path push origin master

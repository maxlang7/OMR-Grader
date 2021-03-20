#!/usr/bin/env bash
source activate grader

trap quitjobs INT
quitjobs() {
    echo ""
    pkill -P $$
    echo "Killed all running jobs".
    scriptCancelled="true"
    trap - INT
    exit
}

# Wait for user input so the jobs can be quit afterwards.
scriptCancelled="false"
waitforcancel() {
    while :
    do
        if [ "$scriptCancelled" == "true" ]; then
            return
        fi

        sleep 1
    done
}

celery -A graderapi worker --loglevel=info &

uwsgi --http :7777 --wsgi-file graderapi.py --mount /=graderapi:flaskapp &

waitforcancel
return 0

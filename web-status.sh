#!/bin/bash

template="web-status.template"
output="/u/mhollen/public_html/web-status.html"

dir='/scratch/cluster/mhollen/single-source'
eval_dir=$dir/evaluations
games=$(cat $dir/games.txt)
ngens=200

function get_gen_data(){
    file=$1
    gen=$2
    d=$(cat $file | cut -d, -f${gen})
    if [[ "$d" == "" ]]; then
        d="NaN"
    fi
    echo $d
}

function get_chart_divs(){
    game=$1
    echo """
    <div class='chartbox'>
      <h3>${game}</h3>
      <div id=\"chart_${game}\" class=\"chart\"></div>
    </div>
    """
}

function get_chart_calls(){
    game=$1

    runs=$(ls $eval_dir/${game}/run-*/fitness.history 2> /dev/null )
    nruns=$(echo $runs | wc -w)
    [[ $nruns -eq 0 ]] && return

    chart_data="["
    for gen in $(seq 1 $ngens); do
        d=""; n=1
        for run in $runs; do
            d="${d}$(get_gen_data $run $gen),"
            n=$((n+1))
        done
        chart_data="${chart_data}[${gen},${d}],"
    done
    chart_data="${chart_data}]"

    echo """
    google.setOnLoadCallback(function() {
        drawCurveTypes('$game','chart_${game}', $chart_data, $nruns);
    });
    """
}

# SCRATCHES
chart_divs=""
chart_calls=""
for game in $games; do
    game_data=$(get_chart_calls $game)
    chart_divs="${chart_divs} <div>"
    if [[ "$game_data" != "" ]]; then
        chart_calls="${chart_calls} $game_data"
        chart_divs="${chart_divs} $(get_chart_divs $game)"
    fi

    # games sourcing games
    for src in $games; do
        [[ "$src" == "$game" ]] && continue
        game_data=$(get_chart_calls $game-using-$src)
        [[ "$game_data" == "" ]] && continue

        chart_calls="${chart_calls} $game_data"
        chart_divs="${chart_divs} $(get_chart_divs $game-using-$src)"
    done

    # games sourcing random
    for src in $games; do
        game_data=$(get_chart_calls $game-using-random-$src)
        [[ "$game_data" == "" ]] && continue

        chart_calls="${chart_calls} $game_data"
        chart_divs="${chart_divs} $(get_chart_divs $game-using-random-$src)"
    done
    chart_divs="${chart_divs} </div> <hr>"
done

tmpfile=$(mktemp)
cp $template $tmpfile
for x in $chart_divs; do
    perl -pi -e "s|CHART_DIVS|${x} CHART_DIVS|" $tmpfile
done
for x in $chart_calls; do 
    perl -pi -e "s|CHART_CALLS|${x} CHART_CALLS|" $tmpfile
done
perl -pi -e "s|CHART_CALLS||" $tmpfile
perl -pi -e "s|CHART_DIVS||" $tmpfile
cp $tmpfile $output
#cat $tmpfile
echo "web-status updated."

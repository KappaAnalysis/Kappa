for i in $(ls -rt *txt)
do
  [[ $i != *"log.txt" ]] && (
  grep "SUCCESS" $i >> /dev/null && echo "+ $i" || echo "- $i"
  )
done
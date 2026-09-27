#!/bin/bash
# Send every line of <dir>/queue.tsv (to<TAB>subject<TAB>body_file) through send_resend.py,
# pausing between sends so the batch doesn't look like bulk mail.
set -u
DIR="$1"; GAP="${2:-45}"
while IFS=$'\t' read -r to subj body; do
  [ -z "$to" ] && continue
  python3 "$(dirname "$0")/send_resend.py" "$to" "$subj" "$DIR/$body" || echo "FAIL $to"
  sleep "$GAP"
done < "$DIR/queue.tsv"
echo "DONE $DIR"

# To automate daily_report.ps1, import this XML into Windows Task Scheduler:
#
# 1. Open Task Scheduler
# 2. Action > Import Task...
# 3. Select schedule_daily_report.xml
# 4. Confirm settings (runs daily at 7:00 AM, highest privileges)
# 5. Save
#
# The task will run daily_report.ps1 automatically every morning.
#
# You can change the time by editing <StartBoundary> in the XML.
#
# To test immediately, right-click the task and choose 'Run'.

@anvil.server.callable
def get_all_data():
    try:
        rows = app_tables.call_statistics.search()

        if not rows:
            print("No rows found in Call Statistics table.")
            return {
                'dates': [],
                'users': [],
                'totals': {},
                'table_data': []
            }

        users_set = set()
        dates_set = set()
        data_by_date_user = {}

        for r in rows:
            user = r['userName'] or "Unknown"
            date = r['reportDate']
            duration = r['totalDuration'] or 0

            if not date:
                print(f"Skipping row with missing date: {r}")
                continue

            users_set.add(user)
            dates_set.add(date)

            if date not in data_by_date_user:
                data_by_date_user[date] = {}
            if user not in data_by_date_user[date]:
                data_by_date_user[date][user] = 0
            data_by_date_user[date][user] += duration

        dates_list = sorted(dates_set)
        users_list = sorted(users_set)

        totals = {u: [] for u in users_list}
        for d in dates_list:
            for u in users_list:
                totals[u].append(data_by_date_user[d].get(u, 0))

        table_data = [
            {
                'userName': r['userName'] or "Unknown",
                'inboundVolume': r['inboundVolume'] or 0,
                'inboundDuration': r['inboundDuration'] or 0,
                'outboundVolume': r['outboundVolume'] or 0,
                'outboundDuration': r['outboundDuration'] or 0,
                'averageDuration': r['averageDuration'] or 0,
                'volume': r['volume'] or 0,
                'totalDuration': r['totalDuration'] or 0,
                'inboundQueueVolume': r['inboundQueueVolume'] or 0,
                'reportDate': r['reportDate']
            }
            for r in rows
        ]

        print(f"Returning data: {len(dates_list)} dates, {len(users_list)} users")
        return {
            'dates': dates_list,
            'users': users_list,
            'totals': totals,
            'table_data': table_data
        }

    except Exception as e:
        print(f"Error in get_all_data: {e}")
        raise

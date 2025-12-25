# ClickHouse Query UI - Fixed!

## What Was Fixed

The "Database Queries" tab in `/home/vergin_jose/Appian_SLA_PS/demo/index.html` now has:

### ✅ Interactive Query Executor
- **Editable SQL textarea** - Write any ClickHouse SQL query
- **Execute button** - Run queries with one click
- **Results table** - See query results in a formatted table
- **Sample query buttons** - Quick access to common queries

### 📊 Sample Queries Available

1. **Total Events** - Count all events in database
2. **Active Cases** - Show currently active cases
3. **SLA Breaches** - Find cases that breached SLA
4. **Queue Depths** - See queue depth per activity
5. **Recent Events** - View last 20 events

### 🎯 How to Use

1. **Open the demo UI**:
   ```bash
   cd /home/vergin_jose/Appian_SLA_PS/demo
   python3 -m http.server 8090
   ```
   Then open: http://localhost:8090

2. **Navigate to "Database Queries" tab**

3. **Click any sample query button** or write your own SQL

4. **Click "Execute Query"** or press `Ctrl+Enter`

5. **View results** in the table below

### 🔧 Technical Details

**Query Execution:**
- Connects directly to ClickHouse HTTP interface (port 8123)
- Uses `FORMAT JSONCompact` for efficient data transfer
- Displays results in a styled table
- Shows row count and execution status

**Sample Query Examples:**

```sql
-- Total events
SELECT count() as total_events FROM events

-- Active cases
SELECT case_id, activity, status, timestamp 
FROM events 
WHERE case_id NOT IN (
    SELECT case_id FROM events 
    WHERE activity IN ('Approve', 'Reject') AND status = 'COMPLETED'
)
ORDER BY timestamp DESC
LIMIT 10

-- Queue depths
SELECT activity, count() as queue_depth
FROM events
WHERE status = 'ASSIGNED'
GROUP BY activity
ORDER BY queue_depth DESC
```

### ⚡ Features

- **Syntax highlighting** - Monospace font for SQL
- **Error handling** - Shows clear error messages
- **Keyboard shortcut** - Ctrl+Enter to execute
- **Responsive table** - Scrollable results
- **Status indicator** - Shows execution progress

### 🐛 Troubleshooting

**If queries don't work:**

1. **Check ClickHouse is running:**
   ```bash
   docker ps | grep clickhouse
   ```

2. **Test ClickHouse HTTP interface:**
   ```bash
   curl 'http://localhost:8123/' -d 'SELECT 1'
   ```

3. **Check browser console** (F12) for CORS errors

4. **Verify data exists:**
   ```bash
   docker exec clickhouse clickhouse-client --query "SELECT count() FROM events"
   ```

### 📝 Custom Queries

You can write any valid ClickHouse SQL query:

```sql
-- Average duration by activity
SELECT 
    activity,
    avg(duration_hours) as avg_duration
FROM events
WHERE duration_hours IS NOT NULL
GROUP BY activity
ORDER BY avg_duration DESC

-- Cases by customer tier
SELECT 
    c4 as priority,
    count(DISTINCT case_id) as case_count
FROM events
GROUP BY c4
ORDER BY case_count DESC

-- Hourly event distribution
SELECT 
    toHour(timestamp) as hour,
    count() as events
FROM events
GROUP BY hour
ORDER BY hour
```

### ✨ UI Improvements Made

1. **Full-width card** - More space for query and results
2. **Textarea instead of input** - Multi-line SQL support
3. **Sample query buttons** - Quick access to common queries
4. **Results display** - Formatted table with headers
5. **Status messages** - Clear feedback on execution
6. **Error display** - Helpful error messages
7. **Scrollable results** - Handle large result sets

## Testing

Open http://localhost:8090 and try:

1. Click "Database Queries" tab
2. Click "Total Events" button
3. Click "Execute Query"
4. See the total event count!

Then try other sample queries or write your own!

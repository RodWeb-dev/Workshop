<?php

$path = __DIR__;

function getActualRealData(SQLite3 $db)
{
    $query = "SELECT * FROM readings WHERE recorded_at = (SELECT MAX(recorded_at) FROM readings)";
    $res = $db->query($query);
    return $res->fetchArray(SQLITE3_ASSOC);
}

function getActualEvent(SQLite3 $db)
{
    $query = "SELECT eq.id, eq.name FROM events AS e
                JOIN equipements AS eq ON e.equipement_id = eq.id
                WHERE e.ended_at IS NULL
                ";
    $res = $db->query($query);
    $events = [];
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $events[] = $row;
    }
    return $events;
}

function getReadings(SQLite3 $db)
{
    $query = "SELECT * FROM (SELECT * FROM readings ORDER BY recorded_at DESC LIMIT 50) ORDER BY recorded_at ASC";
    $res = $db->query($query);
    $readings = [];
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $readings[] = $row;
    }
    return $readings;
}

function getEquipementsStats(SQLite3 $db)
{
    $query = "SELECT equipement_id,
                      COUNT(*) AS cycles,
                      SUM(strftime('%s', COALESCE(ended_at, CURRENT_TIMESTAMP)) - strftime('%s', started_at)) AS duration
                FROM events
                GROUP BY equipement_id";
    $res = $db->query($query);
    $stats = [];
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $stats[$row['equipement_id']] = [
            'cycles' => (int) $row['cycles'],
            'duration' => (int) $row['duration'],
        ];
    }
    return $stats;
}

try {
    $db = new SQLite3($path . '/db/serre.db');

    $actualRealData = getActualRealData($db);
    $actualEvent = getActualEvent($db);
    $readings = getReadings($db);
    $equipementsStats = getEquipementsStats($db);

    http_response_code(200);
    header('Content-Type: application/json');
    echo json_encode([
        'actualRealData' => $actualRealData,
        'actualEvent' => $actualEvent,
        'readings' => $readings,
        'equipementsStats' => $equipementsStats
        ]);
        } catch (Throwable $e) {
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['error' => $e->getMessage()]);
}

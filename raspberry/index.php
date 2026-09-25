<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<?php
function getEquipements(SQLite3 $db)
{
 $query = "SELECT * FROM equipements";
    $res = $db->query($query);
    $equipements = [];
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $equipements[] = $row;
    }
    return $equipements;
}

$db = new SQLite3(__DIR__ . '/db/serre.db');
$equipements = getEquipements($db);

?>
<body>
    <header>
        <h1>SYSTEME DE GESTION DE LA SERRE</h1>
    </header>
    <main>
        <p class="warning">Attention l'accès est réservé aux utilisateurs autorisés.</p>
        <div class="readings-container">
            <h2>Données actuelles</h2>
            <div class="tabs">
                <button class="tab active" data-tab="temp" type="button">
                    <span class="tab-title">Température</span>
                    <span class="tab-value" data-temp-value></span>
                </button>
                <button class="tab" data-tab="hygro" type="button">
                    <span class="tab-title">Humidité</span>
                    <span class="tab-value" data-hygro-value></span>
                </button>
                <button class="tab" data-tab="lux" type="button">
                    <span class="tab-title">Luminosité</span>
                    <span class="tab-value" data-lux-value></span>
                </button>
            </div>
            <div class="tab-panel">
                <canvas id="readingChart"></canvas>
            </div>
        </div>
        <div class="equipements-container">
            <h2>Équipements</h2>
            <div class="equipements">
                <?php foreach($equipements as $equipement): ?>
                    <div class="equipement">
                        <h3><?php echo $equipement['name']; ?></h3>
                        <div class="voyant" data-<?= $equipement['id'] ?>></div>
                        <div class="stats">
                            <span class="cycles" data-cycles-<?= $equipement['id'] ?>>0 cycle</span>
                            <span class="duration" data-duration-<?= $equipement['id'] ?>>0s</span>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </main>
    <footer>
        <p>&copy;Yanis, Mickaël, Omar, Adam et Rodolphe. Tous droits réservés.</p>
    </footer>
    <script src="js/chart.umd.min.js"></script>
    <script src="script.js"></script>
</body>
</html>

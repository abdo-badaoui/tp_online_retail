"""Suite de tests metier pour Atlas Commerce (12 controles)."""
import unittest
from donnees import df, STAT_QUALITE, filtrer, calculer_kpis


class TestAtlasCommerce(unittest.TestCase):
    def test_01_lignes_brutes(self):
        """1. Verifier le nombre de lignes brutes chargees (4 784)."""
        self.assertEqual(STAT_QUALITE["brutes"], 4784)

    def test_02_nettoyage_anomalies(self):
        """2. Verifier l'exclusion des 3 anomalies (4 781 lignes retenues)."""
        self.assertEqual(STAT_QUALITE["retenues"], 4781)
        self.assertEqual(STAT_QUALITE["exclues_total"], 3)
        self.assertEqual(STAT_QUALITE["doublons"], 1)

    def test_03_chiffre_affaires_total(self):
        """3. Verifier le CA total (7 671 306 MAD)."""
        k = calculer_kpis(df)
        self.assertEqual(k["ca"], 7671306.0)

    def test_04_commandes_distinctes(self):
        """4. Verifier le nombre de commandes distinctes (2 400)."""
        k = calculer_kpis(df)
        self.assertEqual(k["commandes"], 2400)

    def test_05_marge_totale(self):
        """5. Verifier la marge commerciale totale (2 607 006 MAD)."""
        k = calculer_kpis(df)
        self.assertEqual(k["marge"], 2607006.0)

    def test_06_panier_moyen(self):
        """6. Verifier le panier moyen (~3 196.38 MAD)."""
        k = calculer_kpis(df)
        self.assertAlmostEqual(k["panier"], 7671306.0 / 2400, places=2)

    def test_07_taux_marque_positif(self):
        """7. Verifier la coherence du taux de marque (> 0)."""
        k = calculer_kpis(df)
        self.assertGreater(k["taux_marque"], 0)
        self.assertLess(k["taux_marque"], 100)

    def test_08_coherence_ca_recalcule(self):
        """8. Verifier la coherence arithmetique de chaque ligne (CA = Q * P * (1-R))."""
        ca_calc = (df["Quantite"] * df["Prix_Unitaire"] * (1 - df["Remise_Pct"])).round(2)
        diff = (df["Chiffre_Affaires"] - ca_calc).abs()
        self.assertTrue((diff <= 0.01).all())

    def test_09_coherence_marge_formule(self):
        """9. Verifier la formule de marge (Marge = CA - Q * Cout)."""
        marge_calc = df["Chiffre_Affaires"] - df["Quantite"] * df["Cout_Unitaire"]
        diff = (df["Marge"] - marge_calc).abs()
        self.assertTrue((diff <= 0.01).all())

    def test_10_filtre_categorie(self):
        """10. Verifier le bon fonctionnement du filtre par categorie."""
        res_mode = filtrer(categorie="Mode")
        self.assertTrue(len(res_mode) > 0)
        self.assertTrue((res_mode["Categorie"] == "Mode").all())

    def test_11_six_regions(self):
        """11. Verifier la presence des 6 regions du catalogue."""
        self.assertEqual(df["Region"].nunique(), 6)

    def test_12_periode_vide(self):
        """12. Verifier le comportement sur filtre sans ventes."""
        vide = filtrer(date_debut="2030-01-01", date_fin="2030-01-02")
        k_vide = calculer_kpis(vide)
        self.assertEqual(k_vide["ca"], 0.0)
        self.assertEqual(k_vide["commandes"], 0)
        self.assertEqual(k_vide["panier"], 0.0)
        self.assertEqual(k_vide["marge"], 0.0)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAtlasCommerce)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    if result.wasSuccessful():
        print(f"{result.testsRun} tests metier : OK")
    else:
        print(f"ECHEC : {len(result.failures)} echecs, {len(result.errors)} erreurs")

import unittest
import os
import json
import shutil
from scripts.mud_client import MUDClient

class TestMUDPersistence(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_data'
        os.makedirs(self.test_dir, exist_ok=True)
        self.client = MUDClient(data_dir=self.test_dir)
        self.player_file = "player.md"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load_state(self):
        data = {"name": "test_player", "level": 10}
        self.client.save_state(self.player_file, data)
        
        loaded_data = self.client.load_state(self.player_file)
        self.assertEqual(loaded_data, data)

if __name__ == '__main__':
    unittest.main()

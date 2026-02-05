import pygame
from player import Player
from config import *

class AIPlayer(Player):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER2_COLOR, "AI Player")
        self.target_x = x
        self.threat_map = {}
        self.decision_cooldown = 0

    def analyze_threats(self, falling_objects):
        threats = []

        for obj in falling_objects:
            distance_to_impact = SCREEN_HEIGHT - obj.y - self.height
            time_to_impact = distance_to_impact / obj.speed if obj.speed > 0 else float('inf')

            future_obj_x = obj.x
            future_obj_y = obj.y + (obj.speed * AI_PREDICTION_LOOKAHEAD)

            horizontal_distance = abs((self.x + self.width // 2) - (future_obj_x + obj.size // 2))

            will_collide = (
                future_obj_y + obj.size >= self.y and
                future_obj_y <= self.y + self.height and
                horizontal_distance < (self.width // 2 + obj.size // 2)
            )

            if obj.y < AI_REACTION_DISTANCE and will_collide:
                threat_level = 1.0 / (time_to_impact + 1)
                threats.append({
                    'object': obj,
                    'threat_level': threat_level,
                    'time_to_impact': time_to_impact,
                    'obj_center_x': obj.x + obj.size // 2
                })

        return sorted(threats, key=lambda t: t['threat_level'], reverse=True)

    def find_safe_zone(self, falling_objects):
        zone_width = 50
        zones = []

        for x in range(0, SCREEN_WIDTH - self.width, zone_width):
            zone_center = x + self.width // 2
            danger_score = 0

            for obj in falling_objects:
                if obj.y < SCREEN_HEIGHT // 2:
                    obj_center = obj.x + obj.size // 2
                    distance = abs(zone_center - obj_center)

                    future_y = obj.y + (obj.speed * 60)
                    if future_y > self.y:
                        if distance < obj.size + self.width:
                            danger_score += (1.0 / (distance + 1)) * 100

            zones.append({
                'x': x,
                'danger_score': danger_score
            })

        safest_zone = min(zones, key=lambda z: z['danger_score'])
        return safest_zone['x']

    def decide_action(self, falling_objects):
        if self.decision_cooldown > 0:
            self.decision_cooldown -= 1
            return

        threats = self.analyze_threats(falling_objects)

        if threats:
            highest_threat = threats[0]
            obj = highest_threat['object']
            obj_center_x = highest_threat['obj_center_x']
            player_center_x = self.x + self.width // 2

            if obj_center_x < player_center_x - 20:
                self.target_x = self.find_safe_zone(falling_objects)
            elif obj_center_x > player_center_x + 20:
                self.target_x = self.find_safe_zone(falling_objects)
            else:
                safe_x = self.find_safe_zone(falling_objects)
                self.target_x = safe_x

            self.decision_cooldown = 5
        else:
            center_x = SCREEN_WIDTH // 2 - self.width // 2
            if abs(self.x - center_x) > 100:
                self.target_x = center_x

    def update(self, falling_objects):
        self.decide_action(falling_objects)

        player_center = self.x + self.width // 2
        target_center = self.target_x + self.width // 2

        if abs(player_center - target_center) > 5:
            direction = 1 if target_center > player_center else -1
            self.move(direction * 0.8)

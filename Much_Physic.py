from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import numpy as np

G = 0.00667

pg.init()

def convert_coords(coords):
    return (coords[0], res[1] - coords[1])

def coerce_in(number: float, range:  tuple[float, float]):
    if number < range[0]:
        return range[0]
    elif number > range[1]:
        return range[1]
    else:
        return number
    
def to_b64(number):
    base64_digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    if number == 0:
        return '0'
    
    base64 = ""
    while number:
        number, remainder = divmod(number, 64)
        base64 = base64_digits[remainder] + base64
    
    return base64

    
font = pg.font.Font("PTSans-Regular.ttf", 25)
smol_font = pg.font.Font("PTSans-Regular.ttf", 15)
text_time_left = 0
text = ""


class Particle:
    def __init__(self, radius, mass, elasticity, num_particles, connected_particle):
        # print(connected_particle)
        self.connected_particle = to_b64(connected_particle)
        self.connected_particle_pos = pg.Vector2(0, 0)
        self.id = to_b64(num_particles)
        self.elasticity = elasticity
        self.radius = radius
        self.mass = mass
        self.pos = pg.Vector2(convert_coords(pg.mouse.get_pos()))
        self.velocity = pg.Vector2(0, 0)
        self.colour = (255,255,255)
        self.acceleration = pg.Vector2(0, 0)
    def update(self, particles):
        self.pos.update(self.pos + (self.velocity * 30 / fps))

        colliding_particle = False

        for particle in particles: 
            if particle.id != self.id:
                between = pg.Vector2(self.pos.x - particle.pos.x, self.pos.y - particle.pos.y)
                opp_between = pg.Vector2(particle.pos.x - self.pos.x, particle.pos.y - self.pos.y)
                # collision
                total_mass = self.mass + particle.mass
                if between.magnitude() <= self.radius + particle.radius:
                    colliding_particle = True
                    # print("Collision")
                    if between.magnitude() < self.radius + particle.radius and between.magnitude() != 0:  
                        try:
                            between.scale_to_length((self.radius + particle.radius + 1))
                        except:
                            between.update(1, 1)
                            between.scale_to_length((self.radius + particle.radius + 1) / 2)
                            opp_between.update(-1, -1)
                        self.pos.x = particle.pos.x + between.x
                        self.pos.y = particle.pos.y + between.y
                    average = (self.velocity + particle.velocity) / 2
                    self.velocity -= average
                    particle.velocity -= average
                    total_speed = self.velocity.magnitude() + particle.velocity.magnitude() * self.elasticity * particle.elasticity
                    speed = ((particle.mass / total_mass) * total_speed)
                    opp_speed = ((self.mass / total_mass) * total_speed)
                    if between.magnitude() != 0:
                        between.scale_to_length(speed)
                    self.velocity.update(between)
                    if opp_between.magnitude() != 0:
                        opp_between.scale_to_length(opp_speed)
                    particle.velocity.update(opp_between)
                    self.velocity += average
                    particle.velocity += average

                opp_between = pg.Vector2(particle.pos.x - self.pos.x, particle.pos.y - self.pos.y)
                if opp_between.magnitude() != 0:
                    force = G*(particle.mass / (opp_between.magnitude() ** 2)) * 30/fps
                    opp_between.scale_to_length(force)
                    self.velocity.update(self.velocity + opp_between)

            if particle.id == self.connected_particle:
                self.connected_particle_pos = particle.pos
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.velocity.y *= -self.elasticity
        if self.pos.y + self.radius < res[1] and not colliding_particle:
            self.velocity.y -= univ_gravity * 30/fps
        elif self.pos.y + self.radius > res[1]:
            self.pos.y = res[1] - self.radius
            self.velocity.y *= -self.elasticity
            self.velocity.y -= univ_gravity

        if self.pos.x - self.radius < 250:
            self.pos.x = 250 + self.radius
            self.velocity.x *= -self.elasticity
        elif self.pos.x + self.radius > res[0]:
            self.pos.x = res[0] - self.radius
            self.velocity.x *= -self.elasticity
                                                

    def show(self, surface: pg.Surface):
        pg.draw.circle(surface, self.colour, convert_coords((self.pos.x, self.pos.y)), self.radius)
        # if self.connected_particle != "":
        #     pg.draw.line(surface, (255, 255, 255), convert_coords(self.pos), convert_coords(self.connected_particle_pos))

class Slider():
    def __init__(self, name: str, var: float, y: float, range: tuple[int, int]):
        self.title = smol_font.render(name, True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(115, 40))
        self.slider = pg.Rect(5, y + 15, 200, 16)
        self.slider_pos = ((particle_size * 4) + 5, y + 15)
        self.sliding = False
        self.text_pos = (220, y + 15)


res = (913, 500)
sim = pg.display.set_mode(res, pg.RESIZABLE + pg.SCALED)

pg.display.set_caption("Much Physic: Particle Simulation")

particles = np.array([])


clock = pg.time.Clock()
paused = False
running = True
mouse_down = False
spamming = False
mouse_prev = (0, 0)
text_time_left = 0


settings_bg = pg.Rect(0, 0, 250, 500)
settings = font.render("SETTINGS", True, (255, 255, 255))
settings_rect = settings.get_rect(center=(115, 15))

particle_size = 20
size = smol_font.render("Particle Size (Px)", True, (255, 255, 255))
size_rect = size.get_rect(center=(115, 40))
size_slider = pg.Rect(5, 55, 200, 16)
size_slider_pos = ((particle_size * 4) + 5, 63)
size_sliding = False
size_text_pos = (220, 55)

particle_weight = 100
weight = smol_font.render("Particle Mass", True, (255, 255, 255))
weight_rect = weight.get_rect(center=(115, 90))
weight_slider = pg.Rect(5, 105, 200, 16)
weight_slider_pos = ((particle_weight / 4) + 5, 113)
weight_sliding = False
weight_text_pos = (220, 105)

particle_elasticity = 0.95
elas = smol_font.render("Particle Elasticity (%)", True, (255, 255, 255))
elas_rect = elas.get_rect(center=(115, 140))
elas_slider = pg.Rect(5, 155, 200, 16)
elas_slider_pos = ((particle_elasticity * 200) + 5, 163)
elas_sliding = False
elas_text_pos = (220, 155)


univ_gravity_scale = 1
univ_gravity = univ_gravity_scale * 0.49
univ = smol_font.render("Universal Gravity Multiplier", True, (255, 255, 255))
univ_rect = univ.get_rect(center=(115, 190))
univ_slider = pg.Rect(5, 205, 200, 16)
univ_slider_pos = ((univ_gravity_scale * 96) + 13, 213)
univ_sliding = False
univ_text_pos = (220, 205)

num_particles = 0

while running:
    fps = clock.get_fps()
    mouse_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                text = "Simulation Reset"
                num_particles = 0
                text_time_left = fps
                particles = np.array([])
            if event.key == pg.K_p or event.key == pg.K_SPACE:
                paused = not paused
                if paused:
                    text = "Simulation Paused"
                    text_time_left = fps
                else:
                    text = "Simulation Resumed"
                    text_time_left = fps
            if paused:
                if event.key == pg.K_PERIOD:
                    text = "Simulation Advanced"
                    text_time_left = fps
                    for particle in particles:
                        particle.update(particles)
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_down = True
            mouse_prev = convert_coords(pg.mouse.get_pos())
            if size_slider.collidepoint(mouse_pos[0], mouse_pos[1]):
                size_sliding = True
            elif weight_slider.collidepoint(mouse_pos[0], mouse_pos[1]):
                weight_sliding = True
            elif elas_slider.collidepoint(mouse_pos[0], mouse_pos[1]):
                elas_sliding = True
            elif univ_slider.collidepoint(mouse_pos[0], mouse_pos[1]):
                univ_sliding = True
        elif event.type == pg.MOUSEBUTTONUP:
            mouse_down = False
            if mouse_prev[0] > 250  and mouse_pos[0] > 250:
                if num_particles == 0:
                    particle = Particle(particle_size, particle_weight, particle_elasticity, num_particles, None)
                else:
                    particle = Particle(particle_size, particle_weight, particle_elasticity, num_particles, num_particles - 1)
                num_particles += 1
                pos = pg.Vector2(convert_coords(mouse_pos))
                mouse_change = pg.Vector2(mouse_prev[0] - pos[0], mouse_prev[1] - pos[1])
                if mouse_change.magnitude() > 5:
                    mouse_change.scale_to_length(mouse_change.magnitude() / 3)
                particle.velocity.update(mouse_change)
                particles = np.append(particles, particle)
                text = "Particle Spawned"
                text_time_left = fps
            size_sliding = False
            weight_sliding = False
            elas_sliding = False
            univ_sliding = False


    sim.fill((25, 25, 25))


    for particle in particles:
        if not paused:
            particle.update(particles)
        particle.show(sim)
    
    if mouse_down:
        if size_sliding:
            size_slider_pos = (coerce_in(mouse_pos[0], (13, 205)), 63)
            particle_size = round(size_slider_pos[0] + 39) / 8
        elif weight_sliding:
            weight_slider_pos = (coerce_in(mouse_pos[0], (13, 205)), 113)
            particle_weight = (weight_slider_pos[0] - 5) * 4
        elif elas_sliding:
            elas_slider_pos = (coerce_in(mouse_pos[0], (13, 205)), 163)
            particle_elasticity = (elas_slider_pos[0] - 5) / 200
        elif univ_sliding:
            univ_slider_pos = (coerce_in(mouse_pos[0], (13, 205)), 213)
            univ_gravity_scale = (univ_slider_pos[0] - 13) / 96
            univ_gravity = univ_gravity_scale * 0.49
        elif spamming:
            particles = np.append(particles, Particle(particle_size, particle_weight, particle_elasticity))
        elif mouse_prev[0] > 250 and mouse_pos[0] > 250:
            pg.draw.line(sim, (255, 255, 255), pg.mouse.get_pos(), convert_coords(mouse_prev))

   

    pg.draw.rect(sim, (50, 50, 50), settings_bg)

    pg.draw.rect(sim, (75, 75, 75), size_slider, border_radius= 7)
    pg.draw.circle(sim, (255, 255, 255), size_slider_pos, 12)

    pg.draw.rect(sim, (75, 75, 75), weight_slider, border_radius= 7)
    pg.draw.circle(sim, (255, 255, 255), weight_slider_pos, 12)

    pg.draw.rect(sim, (75, 75, 75), elas_slider, border_radius= 7)
    pg.draw.circle(sim, (255, 255, 255), elas_slider_pos, 12)

    pg.draw.rect(sim, (75, 75, 75), univ_slider, border_radius= 7)
    pg.draw.circle(sim, (255, 255, 255), univ_slider_pos, 12)

    

    if text_time_left > 0:
        text_time_left -= 1
        text_time = coerce_in(text_time_left / fps, (0, 1))
        sim.blit(font.render(text, True, ((255 - 50) * text_time + 50, (255 - 50) * text_time+ 50, (255 - 50) * text_time + 50)), (10, res[1] - 35))

    sim.blit(settings, settings_rect)

    sim.blit(size, size_rect)
    sim.blit(smol_font.render(str(round(particle_size)), True, (255, 255, 255)), size_text_pos)

    sim.blit(weight, weight_rect)
    sim.blit(smol_font.render(str(round(particle_weight)), True, (255, 255, 255)), weight_text_pos)

    sim.blit(elas, elas_rect)
    sim.blit(smol_font.render(str(round(particle_elasticity, 2)), True, (255, 255, 255)), elas_text_pos)

    sim.blit(univ, univ_rect)
    sim.blit(smol_font.render(str(round(univ_gravity_scale, 2)), True, (255, 255, 255)), univ_text_pos)

    sim.blit(smol_font.render(f"FPS: {round(fps)}", True, (255, 255, 255)), (0,0))
    pg.display.flip()
    # --- Limit to 60 frames per second
    clock.tick_busy_loop()
    # print()
pg.quit()

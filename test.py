#!/usr/bin/env python

from big_ol_pile_of_manim_imports import *
from old_projects.triangle_of_power.triangle import TOP, OPERATION_COLORS
# To watch one of these scenes, run the following:
# python extract_scene.py file_name <SceneName> -p
#
# Use the flat -l for a faster rendering at a lower
# quality, use -s to skip to the end and just show

class Circletoquare(Scene):
    def construct(self):
        circle = Circle()
        self.play()
        self.wait()

class CountingScene(Scene):
    CONFIG = {
        "base" : 10,
        "power_colors" : [YELLOW, MAROON_B, RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position" : (FRAME_X_RADIUS-1)*RIGHT + (FRAME_Y_RADIUS-1)*UP,
        "count_dot_starting_radius" : 0.5,
        "dot_configuration_height" : 2,
        "ones_configuration_location" : UP+2*RIGHT,
        "num_scale_factor" : 2,
        "num_start_location" : 2*DOWN,
    }
    def setup(self):
        self.dots = VGroup()
        self.number = 0        
        self.number_mob = VGroup(TexMobject(str(self.number)))
        self.number_mob.scale(self.num_scale_factor)
        self.number_mob.shift(self.num_start_location)
        self.digit_width = self.number_mob.get_width()

        self.initialize_configurations()
        self.arrows = VGroup()
        self.add(self.number_mob)

    def get_template_configuration(self):
        #This should probably be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        result = []
        for down_right_steps in range(5):
            for left_steps in range(down_right_steps):
                result.append(
                    down_right_steps*down_right + left_steps*LEFT
                )
        return reversed(result[:self.base])

    def get_dot_template(self):
        #This should be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        dots = VGroup(*[
            Dot(
                point, 
                radius = 0.25,
                fill_opacity = 0,
                stroke_width = 2,
                stroke_color = WHITE,
            )
            for point in self.get_template_configuration()
        ])
        dots[-1].set_stroke(width = 0)
        dots.set_height(self.dot_configuration_height)
        return dots

    def initialize_configurations(self):
        self.dot_templates = []
        self.dot_template_iterators = []
        self.curr_configurations = []

    def add_configuration(self):
        new_template = self.get_dot_template()
        new_template.move_to(self.ones_configuration_location)
        left_vect = (new_template.get_width()+LARGE_BUFF)*LEFT
        new_template.shift(
            left_vect*len(self.dot_templates)
        )
        self.dot_templates.append(new_template)
        self.dot_template_iterators.append(
            it.cycle(new_template)
        )
        self.curr_configurations.append(VGroup())

    def count(self, max_val, run_time_per_anim = 1):
        for x in range(max_val):
            self.increment(run_time_per_anim)

    def increment(self, run_time_per_anim = 1, added_anims = [], total_run_time = None):
        run_all_at_once = (total_run_time is not None)
        if run_all_at_once:
            num_rollovers = self.get_num_rollovers()
            run_time_per_anim = float(total_run_time)/(num_rollovers+1)
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius = self.count_dot_starting_radius,
            color = self.power_colors[0],
        )
        moving_dot.generate_target()
        moving_dot.set_fill(opacity = 0)

        continue_rolling_over = True
        place = 0
        self.number += 1
        added_anims = list(added_anims) #Silly python objects...
        added_anims += self.get_new_configuration_animations()
        while continue_rolling_over:          
            moving_dot.target.replace(
                next(self.dot_template_iterators[place])
            )
            if run_all_at_once:
                denom = float(num_rollovers+1)
                start_t = place/denom
                def get_modified_rate_func(anim):
                    return lambda t : anim.original_rate_func(
                        start_t + t/denom
                    )
                for anim in added_anims:
                    if not hasattr(anim, "original_rate_func"):
                        anim.original_rate_func = anim.rate_func
                    anim.rate_func = get_modified_rate_func(anim)
            self.play(
                MoveToTarget(moving_dot), 
                *added_anims, 
                run_time = run_time_per_anim
            )
            self.curr_configurations[place].add(moving_dot)
            if not run_all_at_once:
                added_anims = []


            if len(self.curr_configurations[place].split()) == self.base:
                full_configuration = self.curr_configurations[place]
                self.curr_configurations[place] = VGroup()
                place += 1
                center = full_configuration.get_center_of_mass()
                radius = 0.6*max(
                    full_configuration.get_width(),
                    full_configuration.get_height(),
                )
                circle = Circle(
                    radius = radius,
                    stroke_width = 0,
                    fill_color = self.power_colors[place],
                    fill_opacity = 0.5,
                )
                circle.move_to(center)
                moving_dot = VGroup(circle, full_configuration)
                moving_dot.generate_target()
                moving_dot[0].set_fill(opacity = 0)
            else:
                continue_rolling_over = False
        self.play(*self.get_digit_increment_animations())

    def get_new_configuration_animations(self):
        if self.is_perfect_power():
            self.add_configuration()
            return [FadeIn(self.dot_templates[-1])]
        else:
            return []

    def get_digit_increment_animations(self):
        result = []
        new_number_mob = self.get_number_mob(self.number)
        new_number_mob.move_to(self.number_mob, RIGHT)
        if self.is_perfect_power():
            place = len(new_number_mob.split())-1
            arrow = Arrow(
                new_number_mob[place].get_top(),
                self.dot_templates[place].get_bottom(),
                color = self.power_colors[place]
            )
            self.arrows.add(arrow)
            result.append(ShowCreation(arrow))
        result.append(Transform(
            self.number_mob, new_number_mob,
            submobject_mode = "lagged_start"
        ))
        return result

    def get_number_mob(self, num):
        result = VGroup()
        place = 0
        while num > 0:
            digit = TexMobject(str(num % self.base))
            if place >= len(self.power_colors):
                self.power_colors += self.power_colors
            digit.set_color(self.power_colors[place])
            digit.scale(self.num_scale_factor)
            digit.move_to(result, RIGHT)
            digit.shift(place*(self.digit_width+SMALL_BUFF)*LEFT)
            result.add(digit)
            num /= self.base
            place += 1
        return result

    def is_perfect_power(self):
        number = self.number
        while number > 1:
            if number%self.base != 0:
                return False
            number /= self.base
        return True

    def get_num_rollovers(self):
        next_number = self.number + 1
        result = 0
        while next_number%self.base == 0:
            result += 1
            next_number /= self.base
        return result

class BinaryCountingScene(CountingScene):
    CONFIG = {
        "base" : 2,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+5*RIGHT
    }
    def get_template_configuration(self):
        return [ORIGIN, UP]

class CountInDecimal(CountingScene):
    def construct(self):
        for x in range(11):
            self.increment()
        for x in range(85):
            self.increment(0.25)
        for x in range(20):
            self.increment()

class CountInTernary(CountingScene):
    CONFIG = {
        "base" : 3,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+4*RIGHT
    }
    def construct(self):
        self.count(27)

    # def get_template_configuration(self):
    #     return [ORIGIN, UP]

class CountTo27InTernary(CountInTernary):
    def construct(self):
        for x in range(27):
            self.increment()
        self.wait()

class CountInBinaryTo256(BinaryCountingScene):
    def construct(self):
        self.count(256, 0.25)

class TowersOfHanoiScene(Scene):
    CONFIG = {
        "disk_start_and_end_colors" : [BLUE_E, BLUE_A],
        "num_disks" : 5,
        "peg_width" : 0.25,
        "peg_height" : 2.5,
        "peg_spacing" : 4,
        "include_peg_labels" : True,
        "middle_peg_bottom" : 0.5*DOWN,
        "disk_height" : 0.4,
        "disk_min_width" : 1,
        "disk_max_width" : 3,
        "default_disk_run_time_off_peg" : 1,
        "default_disk_run_time_on_peg" : 2,
    }
    def setup(self):
        self.add_pegs()
        self.add_disks()

    def add_pegs(self):
        peg = Rectangle(
            height = self.peg_height,
            width = self.peg_width, 
            stroke_width = 0,
            fill_color = GREY_BROWN,
            fill_opacity = 1,
        )
        peg.move_to(self.middle_peg_bottom, DOWN)
        self.pegs = VGroup(*[
            peg.copy().shift(vect)
            for vect in (self.peg_spacing*LEFT, ORIGIN, self.peg_spacing*RIGHT)
        ])
        self.add(self.pegs)
        if self.include_peg_labels:
            self.peg_labels = VGroup(*[
                TexMobject(char).next_to(peg, DOWN)
                for char, peg in zip("ABC", self.pegs)
            ])
            self.add(self.peg_labels)

    def add_disks(self):
        self.disks = VGroup(*[
            Rectangle(
                height = self.disk_height,
                width = width,
                fill_color = color,
                fill_opacity = 0.8,
                stroke_width = 0,
            )
            for width, color in zip(
                np.linspace(
                    self.disk_min_width, 
                    self.disk_max_width,
                    self.num_disks
                ),
                color_gradient(
                    self.disk_start_and_end_colors,
                    self.num_disks
                )
            )
        ])
        for number, disk in enumerate(self.disks):
            label = TexMobject(str(number))
            label.set_color(BLACK)
            label.set_height(self.disk_height/2)
            label.move_to(disk)
            disk.add(label)
            disk.label = label
        self.reset_disks(run_time = 0)

        self.add(self.disks)

    def reset_disks(self, **kwargs):
        self.disks.generate_target()
        self.disks.target.arrange_submobjects(DOWN, buff = 0)
        self.disks.target.move_to(self.pegs[0], DOWN)
        self.play(
            MoveToTarget(self.disks), 
            **kwargs
        )
        self.disk_tracker = [
            set(range(self.num_disks)),
            set([]),
            set([])
        ]

    def disk_index_to_peg_index(self, disk_index):
        for index, disk_set in enumerate(self.disk_tracker):
            if disk_index in disk_set:
                return index
        raise Exception("Somehow this disk wasn't accounted for...")

    def min_disk_index_on_peg(self, peg_index):
        disk_index_set = self.disk_tracker[peg_index]
        if disk_index_set:
            return min(self.disk_tracker[peg_index])
        else:
            return self.num_disks

    def bottom_point_for_next_disk(self, peg_index):
        min_disk_index = self.min_disk_index_on_peg(peg_index)
        if min_disk_index >= self.num_disks:
            return self.pegs[peg_index].get_bottom()
        else:
            return self.disks[min_disk_index].get_top()

    def get_next_disk_0_peg(self):
        curr_peg_index = self.disk_index_to_peg_index(0)
        return (curr_peg_index+1)%3

    def get_available_peg(self, disk_index):
        if disk_index == 0:
            return self.get_next_disk_0_peg()
        for index in range(len(list(self.pegs))):
            if self.min_disk_index_on_peg(index) > disk_index:
                return index
        raise Exception("Tower's of Honoi rule broken: No available disks")

    def set_disk_config(self, peg_indices):
        assert(len(peg_indices) == self.num_disks)
        self.disk_tracker = [set([]) for x in range(3)]
        for n, peg_index in enumerate(peg_indices):
            disk_index = self.num_disks - n - 1
            disk = self.disks[disk_index]
            peg = self.pegs[peg_index]
            disk.move_to(peg.get_bottom(), DOWN)
            n_disks_here = len(self.disk_tracker[peg_index])
            disk.shift(disk.get_height()*n_disks_here*UP)
            self.disk_tracker[peg_index].add(disk_index)

    def move_disk(self, disk_index, **kwargs):
        next_peg_index = self.get_available_peg(disk_index)
        self.move_disk_to_peg(disk_index, next_peg_index, **kwargs)

    def move_subtower_to_peg(self, num_disks, next_peg_index, **kwargs):
        disk_indices = list(range(num_disks))
        peg_indices = list(map(self.disk_index_to_peg_index, disk_indices))
        if len(set(peg_indices)) != 1:
            warnings.warn("These disks don't make up a tower right now")
        self.move_disks_to_peg(disk_indices, next_peg_index, **kwargs)

    def move_disk_to_peg(self, disk_index, next_peg_index, **kwargs):
        self.move_disks_to_peg([disk_index], next_peg_index, **kwargs)

    def move_disks_to_peg(self, disk_indices, next_peg_index, run_time = None, stay_on_peg = True, added_anims = []):
        if run_time is None:
            if stay_on_peg is True:
                run_time = self.default_disk_run_time_on_peg
            else:
                run_time = self.default_disk_run_time_off_peg
        disks = VGroup(*[self.disks[index] for index in disk_indices])
        max_disk_index = max(disk_indices)
        next_peg = self.pegs[next_peg_index]        
        curr_peg_index = self.disk_index_to_peg_index(max_disk_index)
        curr_peg = self.pegs[curr_peg_index]
        if self.min_disk_index_on_peg(curr_peg_index) != max_disk_index:
            warnings.warn("Tower's of Hanoi rule broken: disk has crap on top of it")
        target_bottom_point = self.bottom_point_for_next_disk(next_peg_index)
        path_arc = np.sign(curr_peg_index-next_peg_index)*np.pi/3
        if stay_on_peg:
            self.play(
                Succession(
                    ApplyMethod(disks.next_to, curr_peg, UP, 0),
                    ApplyMethod(disks.next_to, next_peg, UP, 0, path_arc = path_arc),
                    ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                ),
                *added_anims,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        else:
            self.play(
                ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                *added_anims,
                path_arc = path_arc*2,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        for disk_index in disk_indices:
            self.disk_tracker[curr_peg_index].remove(disk_index)
            self.disk_tracker[next_peg_index].add(disk_index)

class UdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()


class OpeningManimExample(Scene):
    def construct(self):
        title = TextMobject("This is some \\LaTeX")
        basel = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange_submobjects(DOWN)
        self.play(
            Write(title),
            FadeInFrom(basel, UP),
        )
        self.wait()

        transform_title = TextMobject("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(FadeOutAndShiftDown, basel),
        )
        self.wait()

        grid = NumberPlane()
        grid_title = TextMobject("This is a grid")
        grid_title.scale(1.5)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title),
            FadeInFromDown(grid_title),
            Write(grid),
        )
        self.wait()

        grid_transform_title = TextMobject(
            "That was a non-linear function \\\\"
            "applied to the grid"
        )
        grid_transform_title.move_to(grid_title, UL)
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.apply_function,
            lambda p: p + np.array([
                np.sin(p[1]),
                np.sin(p[0]),
                0,
            ]),
            run_time=3,
        )
        self.wait()
        self.play(
            Transform(grid_title, grid_transform_title)
        )
        self.wait()

class Circletotingting(Scene):
	"""docstring for CircletotiScene"""
	def construct(self):
		circle = Circle()
		randy = Randolph().to_corner()
		buddy = randy.get_bubble()
		buddy.content_scale_factor = 0.8
		buddy.add_content(TOP(2,3,4).scale(0.8))		
		self.add(randy)
		self.play(ShowCreation(circle))
		self.wait()
		self.play(FadeIn(buddy))
		self.wait()

class  Dirthtoway(Scene):

    def construct(self):
        name = Square()
        self.play(ShowCreation(name))
        self.wait()
                


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class Hellomanim(Scene):
	"""docstring for Hellomanim"""
	def construct(self):
		circle = Circle()
		self.play(ShowCreation(circle))
		self.wait()

class DontLearnFromSymbols(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()
        bubble.content_scale_factor = 0.6
        bubble.add_content(TOP(2, 3, 8).scale(0.7))
        equation = VMobject(
            TOP(2, "x"), 
            TexMobject("\\times"),
            TOP(2, "y"),
            TexMobject("="),
            TOP(2, "x+y")
        )
        equation.arrange_submobjects()
        q_marks = TextMobject("???")
        q_marks.set_color(YELLOW)
        q_marks.next_to(randy, UP)

        self.add(randy)
        self.play(FadeIn(bubble))
        self.wait()
        top = bubble.content
        bubble.add_content(equation)
        self.play(
            FadeOut(top),
            ApplyMethod(randy.change_mode, "sassy"),
            Write(bubble.content),
            Write(q_marks),
            run_time = 1
        )
        self.wait(3)


class NotationReflectsMath(Scene):
    def construct(self):
        top_expr = TextMobject("Notation $\\Leftrightarrow$ Math")
        top_expr.shift(2*UP)
        better_questions = TextMobject("Better questions")
        arrow = Arrow(top_expr, better_questions)

        self.play(Write(top_expr))
        self.play(
            ShowCreationPerSubmobject(
                arrow,
                rate_func = lambda t : min(smooth(3*t), 1)
            ),
            Write(better_questions),
            run_time = 3
        )
        self.wait(2)

class AsymmetriesInTheMath(Scene):
    def construct(self):
        assyms_of_top = VMobject(
            TextMobject("Asymmetries of "),
            TOP("a", "b", "c", radius = 0.75).set_color(BLUE)
        ).arrange_submobjects()
        assyms_of_top.to_edge(UP)
        assyms_of_math = TextMobject("""
            Asymmetries of 
            $\\underbrace{a \\cdot a \\cdots a}_{\\text{$b$ times}} = c$
        """)
        VMobject(*assyms_of_math.split()[13:]).set_color(YELLOW)
        assyms_of_math.next_to(assyms_of_top, DOWN, buff = 2)
        rad = TexMobject("\\sqrt{\\quad}").to_edge(LEFT).shift(UP)
        rad.set_color(RED)
        log = TexMobject("\\log").next_to(rad, DOWN)
        log.set_color(RED)

        self.play(FadeIn(assyms_of_top))
        self.wait()
        self.play(FadeIn(assyms_of_math))
        self.wait()
        self.play(Write(VMobject(rad, log)))
        self.wait()

class AddedVsOplussed(Scene):
    def construct(self):
        top = TOP()
        left_times  = top.put_in_vertex(0, TexMobject("\\times"))
        left_dot    = top.put_in_vertex(0, Dot())
        right_times = top.put_in_vertex(2, TexMobject("\\times"))
        right_dot   = top.put_in_vertex(2, Dot())
        plus        = top.put_in_vertex(1, TexMobject("+"))
        oplus       = top.put_in_vertex(1, TexMobject("\\oplus"))
        left_times.set_color(YELLOW)        
        right_times.set_color(YELLOW)        
        plus.set_color(GREEN)        
        oplus.set_color(BLUE)

        self.add(top, left_dot, plus, right_times)
        self.wait()
        self.play(
            Transform(
                VMobject(left_dot, plus, right_times),
                VMobject(right_dot, oplus, left_times),
                path_arc = np.pi/2
            )
        )
        self.wait()



class ReciprocalTop(Scene):
    def construct(self):
        top = TOP()
        start_two = top.put_on_vertex(2, 2)
        end_two = top.put_on_vertex(0, 2)
        x = top.put_on_vertex(1, "x")
        one_over_x = top.put_on_vertex(1, "\\dfrac{1}{x}")
        x.set_color(GREEN)
        one_over_x.set_color(BLUE)
        start_two.set_color(YELLOW)
        end_two.set_color(YELLOW)

        self.add(top, start_two, x)
        self.wait()
        self.play(
            Transform(
                VMobject(start_two, x),
                VMobject(end_two, one_over_x)
            ),
            ApplyMethod(top.rotate, np.pi, UP, path_arc = np.pi/7)
        )
        self.wait()



class NotSymbolicPatterns(Scene):
    def construct(self):
        randy = Randolph()
        symbolic_patterns = TextMobject("Symbolic patterns")
        symbolic_patterns.to_edge(RIGHT).shift(UP)
        line = Line(LEFT, RIGHT, color = RED, stroke_width = 7)
        line.replace(symbolic_patterns)
        substantive_reasoning = TextMobject("Substantive reasoning")
        substantive_reasoning.to_edge(RIGHT).shift(DOWN)

        self.add(randy, symbolic_patterns)
        self.wait()
        self.play(ShowCreation(line))
        self.play(
            Write(substantive_reasoning),
            ApplyMethod(randy.change_mode, "pondering_looking_left"),
            run_time = 1
        )
        self.wait(2)
        self.play(
            ApplyMethod(line.shift, 10*DOWN),
            ApplyMethod(substantive_reasoning.shift, 10*DOWN),
            ApplyMethod(randy.change_mode, "sad"),
            run_time = 1
        )
        self.wait(2)

class ChangeWeCanBelieveIn(Scene):
    def construct(self):
        words = TextMobject("Change we can believe in")
        change = VMobject(*words.split()[:6])
        top = TOP(radius = 0.75)
        top.shift(change.get_right()-top.get_right())

        self.play(Write(words))
        self.play(
            FadeOut(change),
            GrowFromCenter(top)
        )
        self.wait(3)



class TriangleOfPowerIsBetter(Scene):
    def construct(self):
        top = TOP("x", "y", "z", radius = 0.75)
        top.set_color(BLUE)
        alts = VMobject(*list(map(TexMobject, [
            "x^y", "\\log_x(z)", "\\sqrt[y]{z}"
        ])))
        for mob, color in zip(alts.split(), OPERATION_COLORS):
            mob.set_color(color)
        alts.arrange_submobjects(DOWN)
        greater_than = TexMobject(">")
        top.next_to(greater_than, LEFT)
        alts.next_to(greater_than, RIGHT)

        self.play(Write(VMobject(top, greater_than, alts)))
        self.wait()


class InYourOwnNotes(Scene):
    def construct(self):
        anims = [
            self.get_log_anim(3*LEFT), 
            self.get_exp_anim(3*RIGHT), 
        ]
        for anim in anims:
            self.add(anim.mobject)
        self.wait(2)
        self.play(*anims)
        self.wait(2)


    def get_log_anim(self, center):
        O_log_n = TexMobject(["O(", "\\log(n)", ")"])
        O_log_n.shift(center)
        log_n = O_log_n.split()[1]
        #super hacky
        g = log_n.split()[2]
        for mob in g.submobjects:
            mob.is_subpath = False 
            mob.set_fill(BLACK, 1.0)
            log_n.add(mob)
        g.submobjects = []
        #end hack
        top = TOP(2, None, "n", radius = 0.75)
        top.set_width(log_n.get_width())
        top.shift(log_n.get_center())
        new_O_log_n = O_log_n.copy()
        new_O_log_n.submobjects[1] = top
        return Transform(O_log_n, new_O_log_n)


    def get_exp_anim(self, center):
        epii = TexMobject("e^{\\pi i} = -1")
        epii.shift(center)
        top = TOP("e", "\\pi i", "-1", radius = 0.75)
        top.shift(center)
        e, pi, i, equals, minus, one = epii.split()
        ##hacky
        loop = e.submobjects[0]
        loop.is_subpath = False
        loop.set_fill(BLACK, 1.0)
        e.submobjects = []
        ##
        start = VMobject(
            equals,
            VMobject(e, loop), 
            VMobject(pi, i),
            VMobject(minus, one)
        )
        return Transform(start, top)



class Qwerty(Scene):
    def construct(self):
        qwerty = VMobject(
            TextMobject(list("QWERTYUIOP")),
            TextMobject(list("ASDFGHJKL")),
            TextMobject(list("ZXCVBNM")),
        )
        qwerty.arrange_submobjects(DOWN)
        dvorak = VMobject(
            TextMobject(list("PYFGCRL")),
            TextMobject(list("AOEUIDHTNS")),
            TextMobject(list("QJKXBMWVZ")),
        )
        dvorak.arrange_submobjects(DOWN)
        d1, d2, d3 = dvorak.split()
        d1.shift(0.9*RIGHT)
        d3.shift(0.95*RIGHT)

        self.add(qwerty)
        self.wait(2)
        self.play(Transform(qwerty, dvorak))
        self.wait(2)


class ShowLog(Scene):
    def construct(self):
        equation = VMobject(*[
            TOP(2, None, "x"), 
            TexMobject("+"),
            TOP(2, None, "y"),
            TexMobject("="),
            TOP(2, None, "xy")
        ]).arrange_submobjects()
        old_eq = TexMobject("\\log_2(x) + \\log_2(y) = \\log_2(xy)")
        old_eq.to_edge(UP)
        
        self.play(FadeIn(equation))
        self.wait(3)
        self.play(FadeIn(old_eq))
        self.wait(2)


class NoOneWillActuallyDoThis(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = SpeechBubble().pin_to(randy)
        words = TextMobject("No one will actually do this...")
        tau_v_pi = TexMobject("\\tau > \\pi").scale(2)
        morty = Mortimer("speaking").to_corner(DOWN+RIGHT)
        morty_bubble = SpeechBubble(
            direction = RIGHT, 
            height = 4
        )
        morty_bubble.pin_to(morty)
        final_words = TextMobject("If this war is won, it will \\\\ not be won with that attitude")
        lil_thought_bubble = ThoughtBubble(height = 3, width = 5)
        lil_thought_bubble.set_fill(BLACK, 1.0)
        lil_thought_bubble.pin_to(randy)
        lil_thought_bubble.write("Okay buddy, calm down, it's notation \\\\ we're talking about not war.")
        lil_thought_bubble.show()


        self.add(randy)
        self.play(
            ApplyMethod(randy.change_mode, "sassy"),            
            ShowCreation(bubble)
        )
        bubble.add_content(words)
        self.play(Write(words), run_time = 2)
        self.play(Blink(randy))
        bubble.add_content(tau_v_pi)
        self.play(
            FadeOut(words),
            GrowFromCenter(tau_v_pi),
            ApplyMethod(randy.change_mode, "speaking")
        )
        self.remove(words)
        self.play(Blink(randy))
        self.wait(2)
        self.play(
            FadeOut(bubble),
            FadeIn(morty),
            ShowCreation(morty_bubble),
            ApplyMethod(randy.change_mode, "plain")
        )
        morty_bubble.add_content(final_words)
        self.play(Write(final_words))
        self.wait()
        self.play(Blink(morty))
        self.wait(2)
        self.play(ShowCreation(lil_thought_bubble))















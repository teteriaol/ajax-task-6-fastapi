from models.position import Position
from models.dependency import Dependency

class SalaryController:
    def __init__(self):
        self.position_list = {}
        self.dependency_records = []

    def add_new_position(self, position_name, base_salary=0, bonus=0):
        new_position = Position(position_name, base_salary, bonus)
        self.position_list[position_name] = new_position
        return self.pos_to_dict(position_name)

    def delete_position(self, position_name):
        del self.position_list[position_name]
        self.dependency_records = [
            record for record in self.dependency_records 
            if record.from_position != position_name and record.to_position != position_name
        ]

    def get_all_positions(self):
        all_positions = []
        for name in self.position_list:
            all_positions.append(self.pos_to_dict(name))
        return all_positions

    def get_position(self, position_name):
        if position_name in self.position_list:
            return self.pos_to_dict(position_name)
        return None

    def pos_to_dict(self, position_name):
        current_position = self.position_list[position_name]
        levels_data = []
        for level in current_position.levels:
            level_info = {
                'base_salary': level['base_salary'],
                'bonus': level['bonus'],
                'total': level['base_salary'] + level['bonus'],
                'from_position': level['from_position'],
                'from_level': level['from_level'],
                'formula_salary': level['formula_salary'],
                'formula_bonus': level['formula_bonus']
            }
            levels_data.append(level_info)
        return {"name": position_name, "levels": levels_data}

    def create_dependency(self, from_position, from_level, to_position, to_level, formula_salary, formula_bonus):
        for dep in self.dependency_records:
            if dep.from_position == from_position and dep.from_level == from_level:
                dep.to_position = to_position
                dep.to_level = to_level
                dep.formula_salary = formula_salary
                dep.formula_bonus = formula_bonus
                break
        else:
            new_dep = Dependency(from_position, from_level, to_position, to_level, formula_salary, formula_bonus)
            self.dependency_records.append(new_dep)

        if to_position in self.position_list:
            to_position = self.position_list[to_position]
            to_position.set_dependency(to_level, from_position, from_level, formula_salary, formula_bonus)

    def solve_expr(self, formula_str, salary_info):
        if not formula_str:
            return 0

        cleaned_formula = formula_str.replace(' ', '')
        try:
            return float(cleaned_formula)
        except ValueError:
            pass

        working_str = cleaned_formula
        working_str = working_str.replace('S', str(salary_info['S'])).replace('B', str(salary_info['B']))

        while '*' in working_str or '/' in working_str:
            segments = working_str.split('+')
            for idx in range(len(segments)):
                if '*' in segments[idx]:
                    factors = segments[idx].split('*')
                    result = float(factors[0]) * float(factors[1])
                    segments[idx] = str(result)
                elif '/' in segments[idx]:
                    terms = segments[idx].split('/')
                    numerator = float(terms[0])
                    denominator = float(terms[1])
                    if denominator != 0:
                        segments[idx] = str(numerator / denominator)
            working_str = '+'.join(segments)

        if '+' in working_str:
            total = 0
            for part in working_str.split('+'):
                if part:
                    total += float(part)
            return total
        elif '-' in working_str:
            parts = working_str.split('-')
            total = float(parts[0])
            for value in parts[1:]:
                total -= float(value)
            return total
        return float(working_str)

    def calculate_salaries(self):
        salary_results = {}
        for pos_name, pos_obj in self.position_list.items():
            levels_output = []
            for level_data in pos_obj.levels:
                level_calc = {
                    'base_salary': level_data['base_salary'],
                    'bonus': level_data['bonus'],
                    'total': level_data['base_salary'] + level_data['bonus']
                }
                levels_output.append(level_calc)
            salary_results[pos_name] = {'levels': levels_output}

        for _ in range(10): 
            for dependency in self.dependency_records:
                if dependency.from_position not in self.position_list or dependency.to_position not in self.position_list:
                    continue

                from_data = self.position_list[dependency.from_position].get_salary_data(dependency.from_level - 1)
                to_data = self.position_list[dependency.to_position].get_salary_data(dependency.to_level - 1)
                
                input_values = {
                    'S': from_data['base_salary'],
                    'B': from_data['bonus']
                }

                try:
                    updated_salary = self.solve_expr(dependency.formula_salary, input_values)
                    updated_bonus = self.solve_expr(dependency.formula_bonus, input_values)
                except Exception:
                    updated_salary = to_data['base_salary']
                    updated_bonus = to_data['bonus']

                to_data['base_salary'] = updated_salary
                to_data['bonus'] = updated_bonus
                
                if dependency.to_position in salary_results:
                    salary_results[dependency.to_position]['levels'][dependency.to_level - 1] = {
                        'base_salary': updated_salary,
                        'bonus': updated_bonus,
                        'total': updated_salary + updated_bonus
                    }

        return salary_results
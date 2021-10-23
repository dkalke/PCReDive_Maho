import Module.define_value
def week_stage(week):
    if Module.define_value.Stage.one.value <= week and week < Module.define_value.Stage.two.value:
      return 0
    elif Module.define_value.Stage.two.value <= week and week < Module.define_value.Stage.three.value:
      return 1
    elif Module.define_value.Stage.three.value <= week and week < Module.define_value.Stage.four.value:
      return 2
    elif Module.define_value.Stage.four.value <= week and week < Module.define_value.Stage.five.value:
      return 3
    elif Module.define_value.Stage.five.value <= week:
      return 4

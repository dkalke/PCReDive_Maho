import Module.Kernel.define_value
def week_stage(week):
    if Module.Kernel.define_value.Stage.one.value <= week and week < Module.Kernel.define_value.Stage.two.value:
      return 0
    elif Module.Kernel.define_value.Stage.two.value <= week and week < Module.Kernel.define_value.Stage.three.value:
      return 1
    elif Module.Kernel.define_value.Stage.three.value <= week and week < Module.Kernel.define_value.Stage.four.value:
      return 2
    elif Module.Kernel.define_value.Stage.four.value <= week and week < Module.Kernel.define_value.Stage.five.value:
      return 3
    elif Module.Kernel.define_value.Stage.five.value <= week:
      return 4

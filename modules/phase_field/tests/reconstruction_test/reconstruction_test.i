[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 15
  ny = 15
  nz = 0
  xmin = 0
  xmax = 45
  ymin = 0
  ymax = 45
  zmin = 0
  zmax = 0
  elem_type = QUAD4

   uniform_refine = 2
[]

[GlobalParams]
  crys_num = 2
  var_name_base = gr
[]

[Variables]

  [./ReconstructedVariables]    
    EBSD_file_name = al_with_grains.txt
    x1 = 0.0
    y1 = 0.0
    x2 = 45.0
    y2 = 45.0
  [../]
[]

[AuxVariables]

  [./bnds]
    order = FIRST
    family = LAGRANGE
  [../]

  [./grn]
    order = CONSTANT
    family = MONOMIAL
  [../]
[]	     

[Kernels]

  [./PolycrystalKernel]
  [../]
[]

[AuxKernels]
  [./BndsCalc]
    type = BndsCalcAux
    variable = bnds
    execute_on = timestep
  [../]

  [./grn]
    type = GrainIndexAux
    variable = grn
    execute_on = timestep    
  [../]
[]

[BCs]
active = ' '

   [./Periodic]
     [./all]
       auto_direction = 'x y'
     [../]
   [../]

[]

[Materials]
  
  [./CuGrGr]
    type = CuGrGr
    block = 0
    temp = 500 #K
    wGB = 1.5 #micron
    length_scale = 1.0e-6
    time_scale = 1.0e-4
  [../]
[]

[Postprocessors]
  [./ave_gr_area]
    type = PolycrystalAvGrArea
    variable = gr0
  [../]
[]

[Executioner]
  type = Transient
  scheme = 'bdf2'
  petsc_options = '-snes_mf_operator -ksp_monitor -snes_ksp_ew'

  petsc_options_iname = '-pc_type -pc_hypre_type -ksp_gmres_restart'
  petsc_options_value = 'hypre boomeramg 101'
 # petsc_options = '-snes_mf_operator -ksp_monitor -ksp_gmres_modifiedgramschmidt'
 # petsc_options_iname = '-snes_type -snes_ls -ksp_gmres_restart -pc_type  -pc_composite_pcs -sub_0_pc_hypre_type -sub_0_pc_hypre_boomeramg_max_iter -sub_0_pc_hypre_boomeramg_grid_sweeps_all -sub_1_sub_pc_type -pc_composite_type -ksp_type -mat_mffd_type'
 # petsc_options_value = 'ls         basic   201                 composite hypre,asm         boomeramg            2                                  2                                         lu                 multiplicative     fgmres    ds'

  l_tol = 1.0e-4
  l_max_its = 25

  nl_rel_tol = 1.0e-8
  nl_max_its = 20

  start_time = 0.0
  num_steps = 3
  dt = 1.0

  [./Adaptivity]
   initial_adaptivity = 2
    refine_fraction = 0.7
    coarsen_fraction = 0.1
    max_h_level = 2
  [../]
[]

[Output]
  file_base = out
  output_initial = true
  interval = 1
  exodus = true
  perf_log = true
[]
   
    






*** Warning, This code is deprecated and will be removed in future versions!
MOOSE has been updated to include a Moose::registerExecFlags() function, which should be added to the application constructor. It is also possible to add additional flags, see the MooseTestApp.C/h for an example.

Stack frames: 10
0: 0   libmesh_devel.0.dylib               0x000000010594d1e2 libMesh::print_trace(std::__1::basic_ostream<char, std::__1::char_traits<char> >&) + 1506
1: 1   libmoose-devel.0.dylib              0x0000000104cf46cf void moose::internal::mooseDeprecatedStream<libMesh::BasicOStreamProxy<char, std::__1::char_traits<char> >, char const (&) [213]>(libMesh::BasicOStreamProxy<char, std::__1::char_traits<char> >&, char const (&&&) [213]) + 607
2: 2   libmoose-devel.0.dylib              0x0000000104ce4f88 MooseApp::MooseApp(InputParameters) + 2104
3: 3   libmoose_test-devel.0.dylib         0x0000000104780a5d MooseTestApp::MooseTestApp(InputParameters const&) + 45
4: 4   libmoose_test-devel.0.dylib         0x000000010479b3a2 MooseApp* buildApp<MooseTestApp>(InputParameters const&) + 34
5: 5   libmoose-devel.0.dylib              0x0000000104bc9309 AppFactory::create(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, InputParameters, int) + 601
6: 6   libmoose-devel.0.dylib              0x0000000104bc8af3 AppFactory::createApp(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, int, char**) + 435
7: 7   moose_test-devel                    0x0000000104749d6a main + 90
8: 8   libdyld.dylib                       0x00007fffe21c4255 start + 1
9: 9   ???                                 0x0000000000000003 0x0 + 3



[Adaptivity]
  initial_steps = 0 # The number of adaptive steps to do based on the initial condition.
[]


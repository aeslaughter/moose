class Foo
{
public:
  Foo();

  void bar(int input);

  void another(int input, double & output);
};

Foo::bar(int input)
{
  input += 1;
}

Foo::another(int input, double & output)
{
  input += 1;
  output = input * 1.2345;
}

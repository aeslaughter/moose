//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#pragma once

#include <iostream>
#include <numeric>
#include <vector>

namespace StochasticTools
{

/*
 * Custom forward iterator that will skip the supplied entry from the location supplied
 * in the constructor.
 *
 * This follows the design described here:
 * http://www.cplusplus.com/reference/iterator/iterator/
 *
 * However, it uses the C+17 method for defining a custom iterator because the std::iterator class
 * is being deprecated:
 * https://stackoverflow.com/questions/37031805/preparation-for-stditerator-being-deprecated
 *
 * The methods implemented are shown here:
 * http://www.cplusplus.com/reference/iterator/ForwardIterator/
 */
template <typename T>
class skip_iterator
{
public:
  using iterator_category = std::forward_iterator_tag;
  using value_type = T;
  using difference_type = std::ptrdiff_t;
  using pointer = T *;
  using reference = T &;

  skip_iterator(pointer ptr, std::size_t skip = SIZE_MAX);
  skip_iterator(const skip_iterator<value_type> & other);
  skip_iterator<T> operator=(const skip_iterator<value_type> & other);
  ~skip_iterator() = default;

  bool operator==(const skip_iterator<T> & rhs);
  bool operator!=(const skip_iterator<T> & rhs);

  reference operator*();

  skip_iterator<value_type> & operator++();  // prefix
  skip_iterator<value_type> operator++(int); // postfix

private:
  void increment(); // helper for pre/postfix operator++
  pointer _ptr;
  const std::size_t _skip;
  std::size_t _index = 0;
};

template <typename T>
skip_iterator<T>::skip_iterator(T * ptr, std::size_t skip) : _ptr(ptr), _skip(skip)
{
  if (skip == 0)
  {
    _index++;
    _ptr++;
  }
}

template <typename T>
skip_iterator<T>::skip_iterator(const skip_iterator<T> & other)
  : _ptr(other._ptr), _skip(other._skip)
{
  _index = other._index;
}

template <typename T>
skip_iterator<T>
skip_iterator<T>::operator=(const skip_iterator<T> & other)
{
  return skip_iterator<T>(other);
}

template <typename T>
bool
skip_iterator<T>::operator==(const skip_iterator<T> & rhs)
{
  return _ptr == rhs._ptr;
}

template <typename T>
bool
skip_iterator<T>::operator!=(const skip_iterator<T> & rhs)
{
  return _ptr != rhs._ptr;
}

template <typename T>
T & skip_iterator<T>::operator*()
{
  return *_ptr;
}

template <typename T>
skip_iterator<T> & skip_iterator<T>::operator++() // prefix
{
  increment();
  return *this;
}

template <typename T>
skip_iterator<T> skip_iterator<T>::operator++(int) // postfix
{
  skip_iterator<T> it(*this);
  increment();
  return it;
}

template <typename T>
void
skip_iterator<T>::increment()
{
  _ptr++;
  _index++;
  if (_index == _skip)
  {
    _ptr++;
    _index++;
  }
}

template <typename T, typename IterType>
skip_iterator<T>
make_skip_iterator(IterType iter, std::size_t skip = SIZE_MAX)
{
  return skip_iterator<T>(&(*iter), skip);
}
} // namespace

# Frequenz channels Release Notes

## New Features

- There is a new `Receiver.triggered` method that can be used instead of `selected_from`:

  ```python
  async for selected in select(recv1, recv2):
      if recv1.triggered(selected):
          print('Received from recv1:', selected.message)
      if recv2.triggered(selected):
          print('Received from recv2:', selected.message)
  ```

* `Receiver.filter()` can now properly handle `TypeGuard`s. The resulting receiver will now have the narrowed type when a `TypeGuard` is used.

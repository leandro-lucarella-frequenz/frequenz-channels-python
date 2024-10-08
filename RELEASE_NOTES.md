# Frequenz channels Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- There is a new `Receiver.triggered` method that can be used instead of `selected_from`:

  ```python
  async for selected in select(recv1, recv2):
      if recv1.triggered(selected):
          print('Received from recv1:', selected.message)
      if recv2.triggered(selected):
          print('Received from recv2:', selected.message)
  ```

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->

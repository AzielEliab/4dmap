import 'package:flutter/material.dart';

import 'theme.dart';

const limitation =
    'THIS IS an inspection coordinate frame (4DM-WP-1.0). '
    'T Clock, Δ Interval, Γ Trajectory, Π Pattern. '
    'THIS IS NOT a truth engine, Lumen, GIS 4D, or a Node Gate. '
    'Receipts are not truth. No legal name, home, or county on cards. '
    'Author Aziel Eliab.';

void main() {
  runApp(const FourDMapApp());
}

class FourDMapApp extends StatelessWidget {
  const FourDMapApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '4DMap',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const BoardPage(),
    );
  }
}

class BoardPage extends StatefulWidget {
  const BoardPage({super.key});

  @override
  State<BoardPage> createState() => _BoardPageState();
}

class _BoardPageState extends State<BoardPage> {
  String kid =
      'Four axes. Pin a clock on the desktop workbench. '
      'This phone screen does not store a map.';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('4DMap')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(limitation, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 12),
          const Text('truth engine: False · author: Aziel Eliab · bucket: Plain'),
          const SizedBox(height: 16),
          const Text('T Clock · Δ Interval · Γ Trajectory · Π Pattern'),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Pin T on the desktop workbench. Loopback 127.0.0.1:8844.';
                  });
                },
                child: const Text('Pin T'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Span Δ on the desktop. This phone does not store cards.';
                  });
                },
                child: const Text('Span Δ'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Typed joins only. Π→T backdate refuses.';
                  });
                },
                child: const Text('Join'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Silent lens → Π-EMPTY. ZionPattern cap 75%.';
                  });
                },
                child: const Text('Lens'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(kid),
          const SizedBox(height: 24),
          const Text(
            'Not a store listing. Full engine is Python on the desktop. Apache-2.0. '
            'Counted download: 4dmap-download-tracker.vibelock.workers.dev',
          ),
        ],
      ),
    );
  }
}

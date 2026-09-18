import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CostingApp());
}

class CostingApp extends StatelessWidget {
  const CostingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'مركز إدارة التكاليف الموحد (Costing Hub)',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E3A8A),
          brightness: Brightness.light,
        ),
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: MainHubScreen(),
      ),
    );
  }
}

// دالة عامة لنسخ أي كود مع إشعار عائم
void copyCode(BuildContext context, String code, String label) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return;
  Clipboard.setData(ClipboardData(text: code));
  ScaffoldMessenger.of(context).hideCurrentSnackBar();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.check_circle, color: Colors.greenAccent, size: 20),
          const SizedBox(width: 8),
          Text('تم نسخ $label: $code بنجاح!',
              style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
      backgroundColor: const Color(0xFF1E293B),
      duration: const Duration(seconds: 2),
      behavior: SnackBarBehavior.floating,
      width: 360,
    ),
  );
}

// بادج تفاعلي لنسخ الكود بنقرة واحدة
Widget buildCopyBadge(BuildContext context,
    {required String label, required String code, Color? color}) {
  if (code.isEmpty || code.toLowerCase() == 'nan')
    return const SizedBox.shrink();
  final c = color ?? const Color(0xFF1E3A8A);
  return InkWell(
    onTap: () => copyCode(context, code, label),
    borderRadius: BorderRadius.circular(6),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: c.withOpacity(0.08),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: c.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('$label: $code',
              style: TextStyle(
                  fontSize: 11, fontWeight: FontWeight.bold, color: c)),
          const SizedBox(width: 4),
          Icon(Icons.copy_rounded, size: 12, color: c),
        ],
      ),
    ),
  );
}

class MainHubScreen extends StatefulWidget {
  const MainHubScreen({super.key});

  @override
  State<MainHubScreen> createState() => _MainHubScreenState();
}

class _MainHubScreenState extends State<MainHubScreen> {
  int _selectedTabIndex = 0;

  // قواعد البيانات
  List<dynamic> _recipes = [];
  List<dynamic> _staffMeals = [];
  List<dynamic> _talabatItems = [];
  List<dynamic> _odooCatalog = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAllDatabases();
  }

  Future<void> _loadAllDatabases() async {
    try {
      final rStr = await rootBundle.loadString('assets/data/costing_data.json');
      final sStr = await rootBundle.loadString('assets/data/staff_meals.json');
      final tStr = await rootBundle.loadString('assets/data/talabat_mart.json');
      final oStr = await rootBundle.loadString('assets/data/odoo_catalog.json');

      setState(() {
        _recipes = json.decode(rStr);
        _staffMeals = json.decode(sStr);
        _talabatItems = json.decode(tStr);
        _odooCatalog = json.decode(oStr);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.hub_rounded, color: Colors.white),
            const SizedBox(width: 12),
            const Text('مركز إدارة التكاليف والأصناف الموحد',
                style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: Colors.white)),
            const Spacer(),
            Text(
                'أودو: ${_odooCatalog.length} | طلبات: ${_talabatItems.length} | وجبات: ${_recipes.length}',
                style: const TextStyle(fontSize: 12, color: Colors.white70)),
          ],
        ),
        backgroundColor: const Color(0xFF1E3A8A),
      ),
      body: Row(
        children: [
          // شريط التنقل الجانبي
          NavigationRail(
            selectedIndex: _selectedTabIndex,
            onDestinationSelected: (index) =>
                setState(() => _selectedTabIndex = index),
            labelType: NavigationRailLabelType.all,
            backgroundColor: Colors.grey.shade100,
            selectedIconTheme:
                const IconThemeData(color: Color(0xFF1E3A8A), size: 28),
            unselectedIconTheme: IconThemeData(color: Colors.grey.shade600),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.account_tree_outlined),
                selectedIcon: Icon(Icons.account_tree),
                label: Text('شجرة التكاليف'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.restaurant_outlined),
                selectedIcon: Icon(Icons.restaurant),
                label: Text('وجبات الموظفين'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.shopping_bag_outlined),
                selectedIcon: Icon(Icons.shopping_bag),
                label: Text('طلبات مارت'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.inventory_2_outlined),
                selectedIcon: Icon(Icons.inventory_2),
                label: Text('دليل أودو'),
              ),
            ],
          ),
          const VerticalDivider(width: 1),
          // محتوى التبويب النشط
          Expanded(
            child: IndexedStack(
              index: _selectedTabIndex,
              children: [
                _buildRecipesTab(),
                _buildStaffMealsTab(),
                _buildTalabatTab(),
                _buildOdooCatalogTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ==========================================
  // التبويب 1: شجرة التكاليف والـ BOM
  // ==========================================
  Widget _buildRecipesTab() {
    return _UniversalSearchList(
      items: _recipes,
      titleKey: 'name',
      subtitleBuilder: (item) =>
          'Odoo: ${item['odoo_code']} | كود: ${item['item_code']}',
      costBuilder: (item) => (item['calculated_cost'] as num).toDouble(),
      marginBuilder: (item) => (item['profit_margin'] as num).toDouble(),
      detailBuilder: (item) => _buildRecipeDetail(item),
    );
  }

  Widget _buildRecipeDetail(Map<String, dynamic> item) {
    final ings = item['ingredients'] as List? ?? [];
    final cost = (item['calculated_cost'] as num).toDouble();
    final price = (item['markaziya_price'] as num).toDouble();
    final margin = (item['profit_margin'] as num).toDouble();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 2,
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(item['name'],
                          style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1E3A8A))),
                    ),
                    buildCopyBadge(context,
                        label: 'كود Odoo', code: item['odoo_code']),
                    const SizedBox(width: 8),
                    buildCopyBadge(context,
                        label: 'كود الوجبة',
                        code: item['item_code'],
                        color: Colors.indigo),
                  ],
                ),
                const SizedBox(height: 12),
                const Divider(),
                Row(
                  children: [
                    _kpiTile('سعر البيع (المركزية)',
                        '${price.toStringAsFixed(3)} د.أ', Colors.blueGrey),
                    const SizedBox(width: 12),
                    _kpiTile(
                        'التكلفة الكلية الفعلية',
                        '${cost.toStringAsFixed(3)} د.أ',
                        const Color(0xFF1E3A8A)),
                    const SizedBox(width: 12),
                    _kpiTile(
                        'هامش الربح',
                        '${(margin * 100).toStringAsFixed(1)}%',
                        margin >= 0.25
                            ? Colors.green.shade700
                            : Colors.orange.shade800),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text('مكونات الوجبة (${ings.length} مكون):',
            style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Expanded(
          child: ListView.builder(
            itemCount: ings.length,
            itemBuilder: (context, idx) {
              final ing = ings[idx];
              final isSf = ing['is_semi_finished'] == true;
              final subs = ing['sub_ingredients'] as List? ?? [];
              final iCost = (ing['total_cost'] as num).toDouble();

              if (!isSf) {
                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 3),
                  child: ListTile(
                    dense: true,
                    title: Text(ing['name'],
                        style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: Row(
                      children: [
                        Text(
                            'الكمية: ${ing['quantity']} ${ing['unit']} | كلفة الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(4)} د.أ'),
                        const SizedBox(width: 8),
                        buildCopyBadge(context, label: 'ID', code: ing['code']),
                      ],
                    ),
                    trailing: Text('${iCost.toStringAsFixed(3)} د.أ',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                  ),
                );
              }

              return Card(
                color: const Color(0xFFFFFBEB),
                margin: const EdgeInsets.symmetric(vertical: 4),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: BorderSide(color: Colors.amber.shade400),
                ),
                child: ExpansionTile(
                  initiallyExpanded: true,
                  title: Row(
                    children: [
                      Text(ing['name'],
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.brown)),
                      const SizedBox(width: 8),
                      buildCopyBadge(context,
                          label: 'SF كود',
                          code: ing['code'],
                          color: Colors.deepOrange),
                    ],
                  ),
                  subtitle: Text(
                      'الكمية المستخدمة: ${ing['quantity']} ${ing['unit']} | الكلفة: ${iCost.toStringAsFixed(3)} د.أ'),
                  children: subs.map((sub) {
                    return Container(
                      color: Colors.white,
                      child: ListTile(
                        dense: true,
                        title: Text(sub['name']),
                        subtitle: Row(
                          children: [
                            Text(
                                'بالخلطة: ${sub['batch_quantity']} ${sub['unit']} | سعر الوحدة: ${(sub['cost_per_unit'] as num).toStringAsFixed(5)} د.أ'),
                            const SizedBox(width: 8),
                            buildCopyBadge(context,
                                label: 'RM', code: sub['rm_code']),
                          ],
                        ),
                        trailing: Text(
                            '${(sub['total_cost'] as num).toStringAsFixed(4)} د.أ',
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                      ),
                    );
                  }).toList(),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  // ==========================================
  // التبويب 2: وجبات الموظفين
  // ==========================================
  Widget _buildStaffMealsTab() {
    return _UniversalSearchList(
      items: _staffMeals,
      titleKey: 'name',
      subtitleBuilder: (item) => 'كود الوجبة: ${item['code']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      detailBuilder: (item) {
        final ings = item['ingredients'] as List? ?? [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item['name'],
                            style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1E3A8A))),
                        const SizedBox(height: 4),
                        buildCopyBadge(context,
                            label: 'كود الوجبة', code: item['code']),
                      ],
                    ),
                    _kpiTile(
                        'تكلفة الوجبة الكلية',
                        '${(item['total_cost'] as num).toStringAsFixed(3)} د.أ',
                        const Color(0xFF1E3A8A)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: ings.length,
                itemBuilder: (context, idx) {
                  final ing = ings[idx];
                  return Card(
                    child: ListTile(
                      title: Text(ing['name']),
                      subtitle: Row(
                        children: [
                          Text('الكمية: ${ing['quantity']} ${ing['unit']}'),
                          if (ing['code'] != null &&
                              ing['code'].toString().isNotEmpty &&
                              ing['code'].toString().toLowerCase() !=
                                  'nan') ...[
                            const SizedBox(width: 8),
                            buildCopyBadge(context,
                                label: 'كود', code: ing['code'].toString()),
                          ],
                        ],
                      ),
                      trailing: Text(
                          '${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ',
                          style: const TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  // ==========================================
  // التبويب 3: طلبات مارت
  // ==========================================
  Widget _buildTalabatTab() {
    return _UniversalSearchList(
      items: _talabatItems,
      titleKey: 'name',
      subtitleBuilder: (item) => 'القسم: ${item['category']}',
      costBuilder: (item) => (item['price'] as num).toDouble(),
      marginBuilder: (item) => (item['margin'] as num).toDouble(),
      detailBuilder: (item) {
        final price = (item['price'] as num).toDouble();
        final cost = (item['cost'] as num).toDouble();
        final margin = (item['margin'] as num).toDouble();

        return Card(
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'],
                    style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E3A8A))),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    buildCopyBadge(context,
                        label: 'الباركود', code: item['barcode']),
                    buildCopyBadge(context,
                        label: 'SKU', code: item['sku'], color: Colors.indigo),
                    if (item['odoo_code'].toString().isNotEmpty)
                      buildCopyBadge(context,
                          label: 'كود أودو المطابق',
                          code: item['odoo_code'],
                          color: Colors.green.shade800),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _kpiTile('سعر البيع في طلبات',
                        '${price.toStringAsFixed(2)} د.أ', Colors.blueGrey),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'التكلفة المرجعية',
                        '${cost.toStringAsFixed(3)} د.أ',
                        const Color(0xFF1E3A8A)),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'هامش الربح',
                        '${(margin * 100).toStringAsFixed(1)}%',
                        margin >= 0.20
                            ? Colors.green.shade700
                            : Colors.orange.shade800),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ==========================================
  // التبويب 4: دليل أصناف أودو الشامل
  // ==========================================
  Widget _buildOdooCatalogTab() {
    return _UniversalSearchList(
      items: _odooCatalog,
      titleKey: 'name',
      subtitleBuilder: (item) =>
          'كود: ${item['code']} | فئة: ${item['category']}',
      costBuilder: (item) => (item['cost'] as num).toDouble(),
      detailBuilder: (item) {
        return Card(
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'],
                    style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E3A8A))),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    buildCopyBadge(context,
                        label: 'كود أودو', code: item['code']),
                    buildCopyBadge(context,
                        label: 'الباركود',
                        code: item['barcode'],
                        color: Colors.indigo),
                    Chip(label: Text('الفئة: ${item['category']}')),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(),
                Row(
                  children: [
                    _kpiTile(
                        'سعر الشراء / التكلفة',
                        '${(item['cost'] as num).toStringAsFixed(4)} د.أ',
                        const Color(0xFF1E3A8A)),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'سعر البيع الافتراضي',
                        '${(item['price'] as num).toStringAsFixed(3)} د.أ',
                        Colors.blueGrey),
                    const SizedBox(width: 16),
                    _kpiTile('وحدة القياس', item['unit'].toString(),
                        Colors.teal.shade800),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _kpiTile(String title, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: TextStyle(fontSize: 11, color: Colors.grey.shade800)),
            const SizedBox(height: 2),
            Text(value,
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

// قائمة بحث عامة قابلة لإعادة الاستخدام في جميع التبويبات
class _UniversalSearchList extends StatefulWidget {
  final List<dynamic> items;
  final String titleKey;
  final String Function(Map<String, dynamic>) subtitleBuilder;
  final double Function(Map<String, dynamic>)? costBuilder;
  final double Function(Map<String, dynamic>)? marginBuilder;
  final Widget Function(Map<String, dynamic>) detailBuilder;

  const _UniversalSearchList({
    required this.items,
    required this.titleKey,
    required this.subtitleBuilder,
    required this.detailBuilder,
    this.costBuilder,
    this.marginBuilder,
  });

  @override
  State<_UniversalSearchList> createState() => _UniversalSearchListState();
}

class _UniversalSearchListState extends State<_UniversalSearchList> {
  final TextEditingController _ctrl = TextEditingController();
  List<dynamic> _filtered = [];
  Map<String, dynamic>? _selected;

  @override
  void initState() {
    super.initState();
    _filtered = widget.items;
    if (_filtered.isNotEmpty) _selected = _filtered.first;
  }

  void _filter(String q) {
    final query = q.trim().toLowerCase();
    setState(() {
      _filtered = widget.items.where((i) {
        final title = (i[widget.titleKey] ?? '').toString().toLowerCase();
        final code =
            (i['code'] ?? i['sku'] ?? i['barcode'] ?? i['odoo_code'] ?? '')
                .toString()
                .toLowerCase();
        return query.isEmpty || title.contains(query) || code.contains(query);
      }).toList();
      if (_filtered.isNotEmpty && !_filtered.contains(_selected)) {
        _selected = _filtered.first;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 380,
          child: Container(
            color: Colors.grey.shade50,
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(10.0),
                  child: TextField(
                    controller: _ctrl,
                    onChanged: _filter,
                    decoration: InputDecoration(
                      hintText: 'بحث بالاسم أو الكود...',
                      prefixIcon: const Icon(Icons.search),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
                  child: Row(
                    children: [
                      Text('العدد: ${_filtered.length}',
                          style: TextStyle(
                              fontSize: 12, color: Colors.grey.shade700)),
                    ],
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: ListView.separated(
                    itemCount: _filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, idx) {
                      final item = _filtered[idx] as Map<String, dynamic>;
                      final isSel = item == _selected;
                      final cost = widget.costBuilder != null
                          ? widget.costBuilder!(item)
                          : null;
                      final margin = widget.marginBuilder != null
                          ? widget.marginBuilder!(item)
                          : null;

                      return ListTile(
                        dense: true,
                        selected: isSel,
                        selectedTileColor: const Color(0xFFE0E7FF),
                        title: Text(item[widget.titleKey] ?? '',
                            style: TextStyle(
                                fontWeight: isSel
                                    ? FontWeight.bold
                                    : FontWeight.normal)),
                        subtitle: Text(widget.subtitleBuilder(item),
                            style: const TextStyle(fontSize: 11)),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (cost != null)
                              Text('${cost.toStringAsFixed(2)} د.أ',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold)),
                            if (margin != null && margin != 0.0)
                              Text('${(margin * 100).toStringAsFixed(0)}%',
                                  style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: margin >= 0.2
                                          ? Colors.green.shade700
                                          : Colors.orange.shade800)),
                          ],
                        ),
                        onTap: () => setState(() => _selected = item),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
        const VerticalDivider(width: 1),
        Expanded(
          child: _selected == null
              ? const Center(child: Text('اختر عنصراً لعرض التفاصيل'))
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: widget.detailBuilder(_selected!),
                ),
        ),
      ],
    );
  }
}

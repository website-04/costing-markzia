import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CostingApp());
}

// لوحة ألوان المركزية الكلاسيكية المريحة للعين
class MarkaziaTheme {
  static const Color primaryOrange =
      Color(0xFFEA8600); // برتقالي المركزية الذهبي الدافئ
  static const Color primaryDark = Color(0xFFC76F00);
  static const Color darkBar = Color(0xFF1E293B); // كحلي فحمى أنيق
  static const Color bgCream = Color(0xFFFAF8F5); // خلفية عاجية مريحة للعين
  static const Color cardBg = Colors.white;
  static const Color textMain = Color(0xFF1E293B);
  static const Color textSub = Color(0xFF64748B);
  static const Color borderWarm = Color(0xFFEADBCE);
}

class CostingApp extends StatelessWidget {
  const CostingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'المركزية - نظام التكاليف الموحد',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        scaffoldBackgroundColor: MarkaziaTheme.bgCream,
        colorScheme: ColorScheme.fromSeed(
          seedColor: MarkaziaTheme.primaryOrange,
          primary: MarkaziaTheme.primaryOrange,
          surface: MarkaziaTheme.bgCream,
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

// دالة نسخ الأكواد مع إشعار أنيق
void copyCode(BuildContext context, String code, String label) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return;
  Clipboard.setData(ClipboardData(text: code));
  ScaffoldMessenger.of(context).hideCurrentSnackBar();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.check_circle_rounded,
              color: MarkaziaTheme.primaryOrange, size: 20),
          const SizedBox(width: 8),
          Text('تم نسخ $label: $code',
              style: const TextStyle(
                  fontWeight: FontWeight.bold, color: Colors.white)),
        ],
      ),
      backgroundColor: MarkaziaTheme.darkBar,
      duration: const Duration(seconds: 2),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      width: 340,
    ),
  );
}

// بادج تفاعلي لنسخ الكود بنقرة واحدة
Widget buildCopyBadge(BuildContext context,
    {required String label, required String code, Color? color}) {
  if (code.isEmpty || code.toLowerCase() == 'nan')
    return const SizedBox.shrink();
  final c = color ?? MarkaziaTheme.primaryOrange;
  return InkWell(
    onTap: () => copyCode(context, code, label),
    borderRadius: BorderRadius.circular(6),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: c.withOpacity(0.09),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: c.withOpacity(0.4)),
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
        body: Center(
            child:
                CircularProgressIndicator(color: MarkaziaTheme.primaryOrange)),
      );
    }

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 64,
        elevation: 1,
        shadowColor: Colors.black12,
        title: Row(
          children: [
            Image.asset(
              'assets/logo.png',
              height: 44,
              errorBuilder: (_, __, ___) => const Icon(Icons.restaurant_menu,
                  color: MarkaziaTheme.primaryOrange, size: 32),
            ),
            const SizedBox(width: 14),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('الـمـركــزيــة  |  AL-MARKAZIA',
                    style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 17,
                        color: Colors.white)),
                Text('مركز إدارة التكاليف الموحد والشامل',
                    style: TextStyle(fontSize: 11, color: Colors.white70)),
              ],
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white12,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                'أودو: ${_odooCatalog.length}  |  طلبات: ${_talabatItems.length}  |  وجبات: ${_recipes.length}',
                style: const TextStyle(fontSize: 12, color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: MarkaziaTheme.darkBar,
      ),
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _selectedTabIndex,
            onDestinationSelected: (index) =>
                setState(() => _selectedTabIndex = index),
            labelType: NavigationRailLabelType.all,
            backgroundColor: Colors.white,
            selectedIconTheme: const IconThemeData(
                color: MarkaziaTheme.primaryOrange, size: 28),
            unselectedIconTheme: const IconThemeData(color: Colors.black45),
            selectedLabelTextStyle: const TextStyle(
                color: MarkaziaTheme.primaryOrange,
                fontWeight: FontWeight.bold,
                fontSize: 12),
            unselectedLabelTextStyle:
                const TextStyle(color: Colors.black54, fontSize: 11),
            indicatorColor: MarkaziaTheme.primaryOrange.withOpacity(0.12),
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
          const VerticalDivider(width: 1, color: Color(0xFFE2E8F0)),
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
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(18.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(item['name'],
                          style: const TextStyle(
                              fontSize: 21,
                              fontWeight: FontWeight.bold,
                              color: MarkaziaTheme.textMain)),
                    ),
                    buildCopyBadge(context,
                        label: 'Odoo كود', code: item['odoo_code']),
                    const SizedBox(width: 8),
                    buildCopyBadge(context,
                        label: 'كود الوجبة',
                        code: item['item_code'],
                        color: MarkaziaTheme.darkBar),
                  ],
                ),
                const SizedBox(height: 14),
                const Divider(height: 1),
                const SizedBox(height: 14),
                Row(
                  children: [
                    _kpiTile(
                        'سعر البيع (المركزية)',
                        '${price.toStringAsFixed(3)} د.أ',
                        MarkaziaTheme.textSub),
                    const SizedBox(width: 12),
                    _kpiTile(
                        'التكلفة الكلية الدقيقة',
                        '${cost.toStringAsFixed(3)} د.أ',
                        MarkaziaTheme.primaryOrange),
                    const SizedBox(width: 12),
                    _kpiTile(
                        'هامش الربح',
                        '${(margin * 100).toStringAsFixed(1)}%',
                        margin >= 0.25
                            ? Colors.green.shade700
                            : MarkaziaTheme.primaryDark),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text('المكونات التفصيلية (${ings.length} مكون):',
            style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: MarkaziaTheme.textMain)),
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
                  elevation: 0,
                  color: Colors.white,
                  margin: const EdgeInsets.symmetric(vertical: 3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: const BorderSide(color: Color(0xFFEDE8E3)),
                  ),
                  child: ListTile(
                    dense: true,
                    title: Text(ing['name'],
                        style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: Row(
                      children: [
                        Text(
                            'الكمية: ${ing['quantity']} ${ing['unit']} | الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(4)} د.أ'),
                        const SizedBox(width: 8),
                        buildCopyBadge(context, label: 'ID', code: ing['code']),
                      ],
                    ),
                    trailing: Text('${iCost.toStringAsFixed(3)} د.أ',
                        style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: MarkaziaTheme.textMain)),
                  ),
                );
              }

              return Card(
                elevation: 0,
                color: const Color(0xFFFFFBF5),
                margin: const EdgeInsets.symmetric(vertical: 4),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: const BorderSide(color: Color(0xFFF0D5BA)),
                ),
                child: ExpansionTile(
                  initiallyExpanded: true,
                  title: Row(
                    children: [
                      const Icon(Icons.account_tree_rounded,
                          size: 18, color: MarkaziaTheme.primaryOrange),
                      const SizedBox(width: 8),
                      Text(ing['name'],
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: MarkaziaTheme.primaryDark)),
                      const SizedBox(width: 8),
                      buildCopyBadge(context,
                          label: 'SF كود', code: ing['code']),
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
                                'بالخلطة: ${sub['batch_quantity']} ${sub['unit']} | الوحدة: ${(sub['cost_per_unit'] as num).toStringAsFixed(5)} د.أ'),
                            const SizedBox(width: 8),
                            buildCopyBadge(context,
                                label: 'RM', code: sub['rm_code']),
                          ],
                        ),
                        trailing: Text(
                            '${(sub['total_cost'] as num).toStringAsFixed(4)} د.أ',
                            style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                color: MarkaziaTheme.primaryOrange)),
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
  // التبويب 2: وجبات الموظفين المنظمة بالتواريخ
  // ==========================================
  Widget _buildStaffMealsTab() {
    return _UniversalSearchList(
      items: _staffMeals,
      titleKey: 'name',
      subtitleBuilder: (item) => '📅 التاريخ: ${item['date']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      detailBuilder: (item) {
        final ings = item['ingredients'] as List? ?? [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              elevation: 0,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(18.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item['name'],
                            style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                                color: MarkaziaTheme.textMain)),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 3),
                              decoration: BoxDecoration(
                                color: MarkaziaTheme.primaryOrange
                                    .withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text('📅 تاريخ الوجبة: ${item['date']}',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: MarkaziaTheme.primaryDark)),
                            ),
                            const SizedBox(width: 8),
                            buildCopyBadge(context,
                                label: 'كود الوجبة',
                                code: item['code'],
                                color: MarkaziaTheme.darkBar),
                          ],
                        ),
                      ],
                    ),
                    _kpiTile(
                        'تكلفة الوجبة الكلية',
                        '${(item['total_cost'] as num).toStringAsFixed(3)} د.أ',
                        MarkaziaTheme.primaryOrange),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
                'مكونات وجبة الموظف الرسمية المعتمدة من أودو (${ings.length} مكون):',
                style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    color: MarkaziaTheme.textMain)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: ings.length,
                itemBuilder: (context, idx) {
                  final ing = ings[idx];
                  final isSf = ing['is_semi_finished'] == true;
                  final subs = ing['sub_ingredients'] as List? ?? [];

                  if (!isSf) {
                    return Card(
                      elevation: 0,
                      color: Colors.white,
                      margin: const EdgeInsets.symmetric(vertical: 3),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                        side: const BorderSide(color: Color(0xFFEDE8E3)),
                      ),
                      child: ListTile(
                        dense: true,
                        title: Text(ing['name'],
                            style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: MarkaziaTheme.textMain)),
                        subtitle: Row(
                          children: [
                            Text('الكمية: ${ing['quantity']} ${ing['unit']}'),
                            const SizedBox(width: 10),
                            buildCopyBadge(context,
                                label: 'كود المادة', code: ing['code']),
                          ],
                        ),
                        trailing: Text(
                            '${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: MarkaziaTheme.primaryDark)),
                      ),
                    );
                  }

                  return Card(
                    elevation: 0,
                    color: const Color(0xFFFFFBF5),
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                      side: const BorderSide(color: Color(0xFFF0D5BA)),
                    ),
                    child: ExpansionTile(
                      title: Row(
                        children: [
                          const Icon(Icons.account_tree_rounded,
                              size: 16, color: MarkaziaTheme.primaryOrange),
                          const SizedBox(width: 6),
                          Text(ing['name'],
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: MarkaziaTheme.primaryDark)),
                          const SizedBox(width: 8),
                          buildCopyBadge(context,
                              label: 'كود SF', code: ing['code']),
                        ],
                      ),
                      subtitle: Text(
                          'الكمية: ${ing['quantity']} ${ing['unit']} | الإجمالي: ${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ'),
                      children: subs.map((s) {
                        return Container(
                          color: Colors.white,
                          child: ListTile(
                            dense: true,
                            title: Text(s['name']),
                            subtitle: Row(
                              children: [
                                Text(
                                    'الكمية بالخلطة: ${s['batch_quantity']} ${s['unit']}'),
                                const SizedBox(width: 8),
                                buildCopyBadge(context,
                                    label: 'RM', code: s['rm_code']),
                              ],
                            ),
                            trailing: Text(
                                '${(s['total_cost'] as num).toStringAsFixed(3)} د.أ',
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: MarkaziaTheme.primaryOrange)),
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
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'],
                    style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: MarkaziaTheme.textMain)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    buildCopyBadge(context,
                        label: 'الباركود', code: item['barcode']),
                    buildCopyBadge(context,
                        label: 'SKU',
                        code: item['sku'],
                        color: MarkaziaTheme.darkBar),
                    if (item['odoo_code'].toString().isNotEmpty)
                      buildCopyBadge(context,
                          label: 'كود أودو المطابق',
                          code: item['odoo_code'],
                          color: Colors.green.shade800),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(height: 1),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _kpiTile(
                        'سعر البيع في طلبات',
                        '${price.toStringAsFixed(2)} د.أ',
                        MarkaziaTheme.textSub),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'التكلفة المرجعية',
                        '${cost.toStringAsFixed(3)} د.أ',
                        MarkaziaTheme.primaryOrange),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'هامش الربح',
                        '${(margin * 100).toStringAsFixed(1)}%',
                        margin >= 0.20
                            ? Colors.green.shade700
                            : MarkaziaTheme.primaryDark),
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
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'],
                    style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: MarkaziaTheme.textMain)),
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
                        color: MarkaziaTheme.darkBar),
                    Chip(
                      label: Text('الفئة: ${item['category']}',
                          style: const TextStyle(fontSize: 12)),
                      backgroundColor: const Color(0xFFF1F5F9),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(height: 1),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _kpiTile(
                        'سعر التكلفة / الشراء',
                        '${(item['cost'] as num).toStringAsFixed(4)} د.أ',
                        MarkaziaTheme.primaryOrange),
                    const SizedBox(width: 16),
                    _kpiTile(
                        'سعر البيع الافتراضي',
                        '${(item['price'] as num).toStringAsFixed(3)} د.أ',
                        MarkaziaTheme.textSub),
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
          color: color.withOpacity(0.07),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade700)),
            const SizedBox(height: 3),
            Text(value,
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

// قائمة بحث متطورة وسريعة
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
        final date = (i['date'] ?? '').toString().toLowerCase();
        return query.isEmpty ||
            title.contains(query) ||
            code.contains(query) ||
            date.contains(query);
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
          width: 370,
          child: Container(
            color: Colors.white,
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: TextField(
                    controller: _ctrl,
                    onChanged: _filter,
                    decoration: InputDecoration(
                      hintText: 'بحث بالاسم، الكود، أو التاريخ...',
                      prefixIcon: const Icon(Icons.search,
                          color: MarkaziaTheme.primaryOrange),
                      filled: true,
                      fillColor: MarkaziaTheme.bgCream,
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
                  child: Row(
                    children: [
                      Text('إجمالي النتائج: ${_filtered.length}',
                          style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey.shade600)),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                const Divider(height: 1, color: Color(0xFFE2E8F0)),
                Expanded(
                  child: ListView.separated(
                    itemCount: _filtered.length,
                    separatorBuilder: (_, __) =>
                        const Divider(height: 1, color: Color(0xFFF1F5F9)),
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
                        selectedTileColor:
                            MarkaziaTheme.primaryOrange.withOpacity(0.08),
                        title: Text(item[widget.titleKey] ?? '',
                            style: TextStyle(
                              fontWeight:
                                  isSel ? FontWeight.bold : FontWeight.w600,
                              color: isSel
                                  ? MarkaziaTheme.primaryDark
                                  : MarkaziaTheme.textMain,
                            )),
                        subtitle: Text(widget.subtitleBuilder(item),
                            style: TextStyle(
                                fontSize: 11,
                                color: isSel
                                    ? MarkaziaTheme.primaryDark
                                    : MarkaziaTheme.textSub)),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (cost != null)
                              Text('${cost.toStringAsFixed(2)} د.أ',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                      color: MarkaziaTheme.textMain)),
                            if (margin != null && margin != 0.0)
                              Text('${(margin * 100).toStringAsFixed(0)}%',
                                  style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: margin >= 0.2
                                          ? Colors.green.shade700
                                          : MarkaziaTheme.primaryDark)),
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
        const VerticalDivider(width: 1, color: Color(0xFFE2E8F0)),
        Expanded(
          child: _selected == null
              ? const Center(child: Text('اختر عنصراً لعرض تفاصيله الكاملة'))
              : Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: widget.detailBuilder(_selected!),
                ),
        ),
      ],
    );
  }
}

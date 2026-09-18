import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CostingApp());
}

class MarkaziaColors {
  static const Color orange = Color(0xFFFF9C00); // لون المركزية المعتمد #FF9C00
  static const Color dark = Color(0xFF18181B);   // فحمى داكن متناسق مع الشعار الشفاف
  static const Color bg = Color(0xFFFBF9F5);     // خلفية كريمية مريحة
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
        scaffoldBackgroundColor: MarkaziaColors.bg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: MarkaziaColors.orange,
          primary: MarkaziaColors.orange,
          secondary: MarkaziaColors.orange,
          surface: Colors.white,
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

void copyCode(BuildContext context, String code, String label) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return;
  Clipboard.setData(ClipboardData(text: code));
  ScaffoldMessenger.of(context).hideCurrentSnackBar();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          const Icon(Icons.check_circle_rounded, color: MarkaziaColors.orange, size: 20),
          const SizedBox(width: 8),
          Text('تم نسخ $label: $code', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        ],
      ),
      backgroundColor: MarkaziaColors.dark,
      duration: const Duration(seconds: 2),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      width: 320,
    ),
  );
}

Widget buildCopyBadge(BuildContext context, {required String label, required String code, Color? color}) {
  if (code.isEmpty || code.toLowerCase() == 'nan') return const SizedBox.shrink();
  final c = color ?? MarkaziaColors.orange;
  return InkWell(
    onTap: () => copyCode(context, code, label),
    borderRadius: BorderRadius.circular(8),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: c.withOpacity(0.09),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: c.withOpacity(0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('$label: $code', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: c)),
          const SizedBox(width: 5),
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
  List<dynamic> _talabatSheets = [];
  List<dynamic> _odooCatalog = [];
  final Map<String, String> _odooIndex = {};
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

      final oList = json.decode(oStr) as List;
      for (var it in oList) {
        final c = (it['code'] ?? '').toString().trim().toLowerCase();
        final n = (it['name'] ?? '').toString().trim();
        if (c.isNotEmpty && n.isNotEmpty) {
          _odooIndex[c] = n;
        }
      }

      setState(() {
        _recipes = json.decode(rStr);
        _staffMeals = json.decode(sStr);
        _talabatSheets = json.decode(tStr);
        _odooCatalog = oList;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  String getOdooOfficialName(String code, String fallbackName) {
    final c = code.trim().toLowerCase();
    if (_odooIndex.containsKey(c)) {
      return _odooIndex[c]!;
    }
    return fallbackName;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: MarkaziaColors.orange)),
      );
    }

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 68,
        elevation: 0,
        title: Row(
          children: [
            Image.asset(
              'assets/logo.png',
              height: 48,
              fit: BoxFit.contain,
              errorBuilder: (_, __, ___) => const Icon(Icons.restaurant_menu, color: MarkaziaColors.orange, size: 34),
            ),
            const SizedBox(width: 14),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('الـمـركــزيــة  |  AL-MARKAZIA',
                    style: TextStyle(fontWeight: FontWeight.w900, fontSize: 17, color: Colors.white)),
                Text('نظام إدارة وحساب التكاليف الموحد والشامل',
                    style: TextStyle(fontSize: 11, color: Colors.white70)),
              ],
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.12),
                borderRadius: BorderRadius.circular(25),
                border: Border.all(color: Colors.white12),
              ),
              child: Text(
                'أودو الشامل: ${_odooCatalog.length}  |  طلبات مارت: ${_talabatSheets.length} شيت  |  التكاليف: ${_recipes.length}  |  وجبات الموظفين: ${_staffMeals.length}',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: MarkaziaColors.dark,
      ),
      body: Row(
        children: [
          // شريط تنقل ذو حجم ثابت ومغلق هندسياً يمنع اهتزاز الشاشة نهائياً
          SizedBox(
            width: 92,
            child: NavigationRail(
              minWidth: 92,
              minExtendedWidth: 92,
              selectedIndex: _selectedTabIndex,
              onDestinationSelected: (index) => setState(() => _selectedTabIndex = index),
              labelType: NavigationRailLabelType.all,
              backgroundColor: Colors.white,
              selectedIconTheme: const IconThemeData(color: MarkaziaColors.orange, size: 28),
              unselectedIconTheme: const IconThemeData(color: Colors.black45),
              selectedLabelTextStyle: const TextStyle(color: MarkaziaColors.orange, fontWeight: FontWeight.bold, fontSize: 11),
              unselectedLabelTextStyle: const TextStyle(color: Colors.black54, fontWeight: FontWeight.bold, fontSize: 11),
              indicatorColor: MarkaziaColors.orange.withOpacity(0.15),
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.account_tree_outlined),
                  selectedIcon: Icon(Icons.account_tree_rounded),
                  label: Text('شجرة التكاليف'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.restaurant_outlined),
                  selectedIcon: Icon(Icons.restaurant_rounded),
                  label: Text('وجبات الموظفين'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.shopping_bag_outlined),
                  selectedIcon: Icon(Icons.shopping_bag_rounded),
                  label: Text('طلبات مارت'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.inventory_2_outlined),
                  selectedIcon: Icon(Icons.inventory_2_rounded),
                  label: Text('دليل أودو'),
                ),
              ],
            ),
          ),
          const VerticalDivider(width: 1, thickness: 1, color: Color(0xFFE2E8F0)),
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

  // 1. شجرة التكاليف
  Widget _buildRecipesTab() {
    return _UniversalSearchList(
      items: _recipes,
      titleKey: 'name',
      subtitleBuilder: (item) => 'Odoo: ${item['odoo_code']} | كود: ${item['item_code']}',
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
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item['name'],
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          buildCopyBadge(context, label: 'Odoo كود', code: item['odoo_code']),
                          const SizedBox(width: 8),
                          buildCopyBadge(context, label: 'كود الوجبة', code: item['item_code'], color: MarkaziaColors.dark),
                        ],
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                  decoration: BoxDecoration(
                    color: MarkaziaColors.orange.withOpacity(0.09),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: MarkaziaColors.orange.withOpacity(0.35)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('التكلفة الكلية الفعلية', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey.shade700)),
                      const SizedBox(height: 3),
                      Text('${cost.toStringAsFixed(3)} د.أ',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: MarkaziaColors.orange)),
                      Text('سعر البيع: ${price.toStringAsFixed(3)} د.أ  |  هامش: ${(margin * 100).toStringAsFixed(1)}%',
                          style: TextStyle(fontSize: 11, color: margin >= 0.25 ? Colors.green.shade700 : MarkaziaColors.orange)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 14),
        Text('المكونات التفصيلية (${ings.length} صنف):',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: MarkaziaColors.dark)),
        const SizedBox(height: 8),
        Expanded(
          child: ListView.builder(
            itemCount: ings.length,
            itemBuilder: (context, idx) {
              final ing = ings[idx];
              final isSf = ing['is_semi_finished'] == true;
              final subs = ing['sub_ingredients'] as List? ?? [];
              final iCost = (ing['total_cost'] as num).toDouble();
              final officialName = getOdooOfficialName(ing['code'] ?? '', ing['name'] ?? '');

              if (!isSf) {
                return Card(
                  elevation: 0,
                  color: Colors.white,
                  margin: const EdgeInsets.symmetric(vertical: 3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  child: ListTile(
                    dense: true,
                    title: Text(officialName, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Row(
                      children: [
                        Text('الكمية: ${ing['quantity']} ${ing['unit']} | الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(4)} د.أ'),
                        const SizedBox(width: 10),
                        buildCopyBadge(context, label: 'ID', code: ing['code']),
                      ],
                    ),
                    trailing: Text('${iCost.toStringAsFixed(3)} د.أ',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: MarkaziaColors.dark)),
                  ),
                );
              }

              return Card(
                elevation: 0,
                color: const Color(0xFFFFFDF8),
                margin: const EdgeInsets.symmetric(vertical: 4),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: BorderSide(color: MarkaziaColors.orange.withOpacity(0.4)),
                ),
                child: ExpansionTile(
                  initiallyExpanded: true,
                  title: Row(
                    children: [
                      const Icon(Icons.account_tree_rounded, size: 18, color: MarkaziaColors.orange),
                      const SizedBox(width: 8),
                      Text(officialName, style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                      const SizedBox(width: 8),
                      buildCopyBadge(context, label: 'SF كود', code: ing['code']),
                    ],
                  ),
                  subtitle: Text('الكمية المستخدمة: ${ing['quantity']} ${ing['unit']} | الكلفة: ${iCost.toStringAsFixed(3)} د.أ'),
                  children: subs.map((sub) {
                    final subOfficial = getOdooOfficialName(sub['rm_code'] ?? '', sub['name'] ?? '');
                    return Container(
                      color: Colors.white,
                      child: ListTile(
                        dense: true,
                        title: Text(subOfficial),
                        subtitle: Row(
                          children: [
                            Text('بالخلطة: ${sub['standard_quantity']} ${sub['unit']}'),
                            const SizedBox(width: 8),
                            buildCopyBadge(context, label: 'RM', code: sub['rm_code']),
                          ],
                        ),
                        trailing: Text('${(sub['total_cost'] as num).toStringAsFixed(4)} د.أ',
                            style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
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

  // 2. وجبات الموظفين بالحجمين والأسماء الصريحة
  Widget _buildStaffMealsTab() {
    return _UniversalSearchList(
      items: _staffMeals,
      titleKey: 'name',
      subtitleBuilder: (item) => '${item['date']}  |  ${(item['ingredients'] as List? ?? []).length} مكونات',
      isStaffTab: true,
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
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(item['name'],
                              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                decoration: BoxDecoration(
                                  color: MarkaziaColors.orange.withOpacity(0.09),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: MarkaziaColors.orange.withOpacity(0.3)),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.calendar_today_rounded, size: 13, color: MarkaziaColors.orange),
                                    const SizedBox(width: 6),
                                    Text('تاريخ الوجبة: ${item['date']}',
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: MarkaziaColors.orange)),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 10),
                              buildCopyBadge(context, label: 'كود الوجبة', code: item['code'], color: MarkaziaColors.dark),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                      decoration: BoxDecoration(
                        color: MarkaziaColors.orange.withOpacity(0.09),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: MarkaziaColors.orange.withOpacity(0.35)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text('تكلفة الوجبة الكلية', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey.shade700)),
                          const SizedBox(height: 3),
                          Text('${(item['total_cost'] as num).toStringAsFixed(3)} د.أ',
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: MarkaziaColors.orange)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 14),
            Text('المكونات التفصيلية (الحجم الفعلي المستخدم للطبخة مقابل الحجم المعياري):',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: MarkaziaColors.dark)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: ings.length,
                itemBuilder: (context, idx) {
                  final ing = ings[idx];
                  final isSf = ing['is_semi_finished'] == true;
                  final subs = ing['sub_ingredients'] as List? ?? [];
                  final officialName = getOdooOfficialName(ing['code'] ?? '', ing['name'] ?? '');

                  if (!isSf) {
                    return Card(
                      elevation: 0,
                      color: Colors.white,
                      margin: const EdgeInsets.symmetric(vertical: 4),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: const BorderSide(color: Color(0xFFE2E8F0)),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        child: Row(
                          children: [
                            Container(
                              width: 8, height: 8,
                              decoration: const BoxDecoration(color: MarkaziaColors.orange, shape: BoxShape.circle),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(officialName,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: MarkaziaColors.dark)),
                                  const SizedBox(height: 4),
                                  Wrap(
                                    spacing: 12,
                                    children: [
                                      Text('الحجم الفعلي للطبخة: ${ing['actual_quantity']} ${ing['unit']}',
                                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                                      Text('المعياري: ${ing['standard_quantity']}',
                                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                                      buildCopyBadge(context, label: 'كود', code: ing['code']),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text('${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ',
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.orange)),
                                Text('الوحدة: ${(ing['cost_per_unit'] as num).toStringAsFixed(3)} د.أ',
                                    style: TextStyle(fontSize: 11, color: Colors.grey.shade500)),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  }

                  return Card(
                    elevation: 0,
                    color: const Color(0xFFFFFDF8),
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: MarkaziaColors.orange.withOpacity(0.4)),
                    ),
                    child: ExpansionTile(
                      title: Row(
                        children: [
                          const Icon(Icons.account_tree_rounded, size: 16, color: MarkaziaColors.orange),
                          const SizedBox(width: 8),
                          Text(officialName, style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
                          const SizedBox(width: 8),
                          buildCopyBadge(context, label: 'SF كود', code: ing['code']),
                        ],
                      ),
                      subtitle: Row(
                        children: [
                          Text('الفعلي: ${ing['actual_quantity']} ${ing['unit']}  |  ',
                              style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                          Text('المعياري: ${ing['standard_quantity']}  |  الإجمالي: ${(ing['total_cost'] as num).toStringAsFixed(3)} د.أ'),
                        ],
                      ),
                      children: subs.map((s) {
                        final sOfficial = getOdooOfficialName(s['rm_code'] ?? '', s['name'] ?? '');
                        return Container(
                          color: Colors.white,
                          child: ListTile(
                            dense: true,
                            title: Text(sOfficial),
                            subtitle: Row(
                              children: [
                                Text('المعياري بالخلطة: ${s['standard_quantity']} ${s['unit']}'),
                                const SizedBox(width: 8),
                                buildCopyBadge(context, label: 'RM', code: s['rm_code']),
                              ],
                            ),
                            trailing: Text('${(s['total_cost'] as num).toStringAsFixed(4)} د.أ',
                                style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange)),
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

  // 3. طلبات مارت: شيتات تواريخ أشهر 8 و 9 وشيت حسبة الخروف المعتمد
  Widget _buildTalabatTab() {
    if (_talabatSheets.isEmpty) {
      return const Center(child: Text('جاري تحميل شيتات طلبات مارت...'));
    }

    return _TalabatBrowser(sheets: _talabatSheets);
  }

  // 4. دليل أودو الشامل: الكود، الاسم، الكمية، كلفة الكمية، الإجمالي
  Widget _buildOdooCatalogTab() {
    return _UniversalSearchList(
      items: _odooCatalog,
      titleKey: 'name',
      subtitleBuilder: (item) => 'كود: ${item['code']} | فئة: ${item['category']}',
      costBuilder: (item) => (item['total_cost'] as num).toDouble(),
      detailBuilder: (item) {
        return Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'], style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    buildCopyBadge(context, label: 'كود أودو', code: item['code']),
                    if (item['barcode'].toString().isNotEmpty)
                      buildCopyBadge(context, label: 'الباركود', code: item['barcode'], color: MarkaziaColors.dark),
                    Chip(
                      label: Text('الفئة: ${item['category']}', style: const TextStyle(fontSize: 12)),
                      backgroundColor: const Color(0xFFF8FAFC),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(height: 1),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _kpiTile('الكمية', '${item['quantity']} ${item['unit']}', Colors.indigo.shade800),
                    const SizedBox(width: 16),
                    _kpiTile('كلفة الوحدة (الشراء)', '${(item['cost_per_unit'] as num).toStringAsFixed(3)} د.أ', Colors.grey.shade700),
                    const SizedBox(width: 16),
                    _kpiTile('إجمالي كلفة الكمية', '${(item['total_cost'] as num).toStringAsFixed(3)} د.أ', MarkaziaColors.orange),
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
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey.shade600)),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

// مستعرض شيتات وتواريخ طلبات مارت
class _TalabatBrowser extends StatefulWidget {
  final List<dynamic> sheets;
  const _TalabatBrowser({required this.sheets});

  @override
  State<_TalabatBrowser> createState() => _TalabatBrowserState();
}

class _TalabatBrowserState extends State<_TalabatBrowser> {
  int _selectedSheetIdx = 0;

  @override
  Widget build(BuildContext context) {
    final currentSheet = widget.sheets[_selectedSheetIdx] as Map<String, dynamic>;
    final isLamb = currentSheet['type'] == 'lamb_report';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // شريط اختيار التاريخ والشيت (شهر 8 و 9)
        Container(
          height: 60,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: Colors.white,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: widget.sheets.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (context, idx) {
              final sh = widget.sheets[idx];
              final isSel = idx == _selectedSheetIdx;
              final isL = sh['type'] == 'lamb_report';

              return ChoiceChip(
                selected: isSel,
                selectedColor: MarkaziaColors.orange,
                backgroundColor: const Color(0xFFFBF9F5),
                avatar: Icon(isL ? Icons.receipt_long : Icons.calendar_today_rounded,
                    size: 14, color: isSel ? Colors.white : MarkaziaColors.orange),
                label: Text(sh['display_title'] ?? sh['sheet_name'],
                    style: TextStyle(
                      fontSize: 12, fontWeight: FontWeight.bold,
                      color: isSel ? Colors.white : MarkaziaColors.dark,
                    )),
                onSelected: (val) {
                  if (val) setState(() => _selectedSheetIdx = idx);
                },
              );
            },
          ),
        ),
        const Divider(height: 1, thickness: 1, color: Color(0xFFE2E8F0)),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(22.0),
            child: isLamb ? _buildLambReport(currentSheet) : _buildDailySheet(currentSheet),
          ),
        ),
      ],
    );
  }

  Widget _buildLambReport(Map<String, dynamic> data) {
    final cuts = data['cuts'] as List? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: Padding(
            padding: const EdgeInsets.all(22.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(color: MarkaziaColors.orange.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
                      child: const Icon(Icons.receipt_long_rounded, color: MarkaziaColors.orange, size: 28),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('حسبة تفصيل وتقطيع الخروف (${data['sheet_name']})',
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                        const Text('المطابقة الرسمية للفاتورة والأوزان والقطعيات', style: TextStyle(fontSize: 12, color: Colors.black54)),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                const Divider(height: 1),
                const SizedBox(height: 18),
                Row(
                  children: [
                    _kpiTile('عدد الخرفان', '${data['sheep_count']} خروف', Colors.grey.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('سعر الكيلو (فاتورة)', '${data['price_per_kg']} د.أ', Colors.blueGrey.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('إجمالي الفاتورة', '${data['invoice_total']} د.أ', MarkaziaColors.orange),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _kpiTile('الوزن عند الاستلام (الفاتورة)', '${data['weight_received']} كغ', Colors.grey.shade700),
                    const SizedBox(width: 12),
                    _kpiTile('الوزن قبل التقطيع', '${data['weight_cut']} كغ', Colors.indigo.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('الفاقد بالتقطيع', '${data['waste_loss']} كغ', Colors.red.shade800),
                    const SizedBox(width: 12),
                    _kpiTile('صافي الوزن بعد التقطيع', '${data['weight_cut']} كغ', Colors.green.shade800),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text('جدول تفصيل القطعيات وأسعارها وإجمالياتها:',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: MarkaziaColors.dark)),
        const SizedBox(height: 10),
        Card(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Table(
              columnWidths: const {
                0: FlexColumnWidth(2.8), 1: FlexColumnWidth(1.2),
                2: FlexColumnWidth(1.0), 3: FlexColumnWidth(1.2), 4: FlexColumnWidth(1.5),
              },
              children: [
                TableRow(
                  decoration: const BoxDecoration(color: Color(0xFFF3F4F6)),
                  children: const [
                    Padding(padding: EdgeInsets.all(14.0), child: Text('اسم الصنف / القطعية', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('الكمية (كغ)', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('النسبة %', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('السعر (د.أ)', style: TextStyle(fontWeight: FontWeight.bold))),
                    Padding(padding: EdgeInsets.all(14.0), child: Text('الإجمالي (د.أ)', style: TextStyle(fontWeight: FontWeight.bold))),
                  ],
                ),
                ...cuts.map<TableRow>((c) {
                  Color rowBg = Colors.white;
                  if (c['status'] == 'highlight_yellow') rowBg = const Color(0xFFFEF9C3);
                  if (c['status'] == 'highlight_red') rowBg = const Color(0xFFFEE2E2);

                  return TableRow(
                    decoration: BoxDecoration(color: rowBg, border: const Border(top: BorderSide(color: Color(0xFFF1F5F9)))),
                    children: [
                      Padding(padding: const EdgeInsets.all(12.0), child: Text(c['name'].toString(), style: const TextStyle(fontWeight: FontWeight.w600))),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text('${c['qty']} كغ')),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text(c['percentage'].toString(), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black54))),
                      Padding(padding: const EdgeInsets.all(12.0), child: Text('${c['price']} د.أ')),
                      Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Text('${(c['total'] as num).toStringAsFixed(3)} د.أ',
                            style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                      ),
                    ],
                  );
                }).toList(),
                TableRow(
                  decoration: const BoxDecoration(color: Color(0xFF18181B)),
                  children: [
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('المجموع الإجمالي للقطعيات الصافية', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white))),
                    Padding(padding: const EdgeInsets.all(14.0), child: Text('${data['weight_cut']} كغ', style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange))),
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('100%', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white70))),
                    const Padding(padding: EdgeInsets.all(14.0), child: Text('—', style: TextStyle(color: Colors.white54))),
                    Padding(
                      padding: const EdgeInsets.all(14.0),
                      child: Text('${data['cuts_total_value']} د.أ',
                          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: MarkaziaColors.orange)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDailySheet(Map<String, dynamic> data) {
    final items = data['items'] as List? ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 0, color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(data['display_title'] ?? 'كشف طلبات', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: MarkaziaColors.dark)),
                      const SizedBox(height: 4),
                      Text('إجمالي الأصناف: ${data['items_count']} صنف', style: const TextStyle(color: Colors.black54)),
                    ],
                  ),
                ),
                _kpiTile('إجمالي المبيعات', '${(data['total_sales'] as num).toStringAsFixed(3)} د.أ', MarkaziaColors.orange),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          elevation: 0, color: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Color(0xFFE2E8F0))),
          child: DataTable(
            headingRowColor: MaterialStateProperty.all(const Color(0xFFFBF9F5)),
            columns: const [
              DataColumn(label: Text('اسم الصنف', style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(label: Text('SKU', style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(label: Text('الكمية', style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(label: Text('السعر', style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(label: Text('الإجمالي', style: TextStyle(fontWeight: FontWeight.bold))),
            ],
            rows: items.map<DataRow>((it) {
              return DataRow(cells: [
                DataCell(Text(it['name'].toString(), style: const TextStyle(fontWeight: FontWeight.w600))),
                DataCell(Text(it['sku'].toString())),
                DataCell(Text('${it['quantity']}')),
                DataCell(Text('${it['price']} د.أ')),
                DataCell(Text('${(it['total'] as num).toStringAsFixed(3)} د.أ', style: const TextStyle(fontWeight: FontWeight.bold, color: MarkaziaColors.orange))),
              ]);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _kpiTile(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08), borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey.shade600)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }
}

class _UniversalSearchList extends StatefulWidget {
  final List<dynamic> items;
  final String titleKey;
  final String Function(Map<String, dynamic>) subtitleBuilder;
  final double Function(Map<String, dynamic>)? costBuilder;
  final double Function(Map<String, dynamic>)? marginBuilder;
  final Widget Function(Map<String, dynamic>) detailBuilder;
  final bool isStaffTab;

  const _UniversalSearchList({
    required this.items,
    required this.titleKey,
    required this.subtitleBuilder,
    required this.detailBuilder,
    this.costBuilder,
    this.marginBuilder,
    this.isStaffTab = false,
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

  @override
  void didUpdateWidget(covariant _UniversalSearchList oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.items != widget.items) {
      _filter(_ctrl.text);
    }
  }

  void _filter(String q) {
    final query = q.trim().toLowerCase();
    setState(() {
      _filtered = widget.items.where((i) {
        final title = (i[widget.titleKey] ?? '').toString().toLowerCase();
        final code = (i['code'] ?? i['sku'] ?? i['barcode'] ?? i['odoo_code'] ?? '').toString().toLowerCase();
        final date = (i['date'] ?? '').toString().toLowerCase();

        final ings = (i['ingredients'] as List? ?? []);
        final ingMatch = ings.any((ing) {
          final n = (ing['name'] ?? '').toString().toLowerCase();
          final c = (ing['code'] ?? '').toString().toLowerCase();
          final r = (ing['raw_description'] ?? '').toString().toLowerCase();
          return n.contains(query) || c.contains(query) || r.contains(query);
        });

        return query.isEmpty || title.contains(query) || code.contains(query) || date.contains(query) || ingMatch;
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
          width: 365,
          child: Container(
            color: Colors.white,
            child: Column(
              children: [
                Container(
                  margin: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFBF9F5),
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: TextField(
                    controller: _ctrl,
                    onChanged: _filter,
                    decoration: InputDecoration(
                      hintText: 'بحث بالاسم، الكود، التاريخ، أو المادة...',
                      prefixIcon: const Icon(Icons.search_rounded, color: MarkaziaColors.orange),
                      suffixIcon: _ctrl.text.isNotEmpty
                          ? IconButton(icon: const Icon(Icons.clear, size: 16), onPressed: () { _ctrl.clear(); _filter(''); })
                          : null,
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 2),
                  child: Row(
                    children: [
                      Text('إجمالي النتائج: ${_filtered.length}',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey.shade500)),
                    ],
                  ),
                ),
                const SizedBox(height: 6),
                const Divider(height: 1, thickness: 1, color: Color(0xFFE2E8F0)),
                Expanded(
                  child: ListView.separated(
                    itemCount: _filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, thickness: 1, color: Color(0xFFF8FAFC)),
                    itemBuilder: (context, idx) {
                      final item = _filtered[idx] as Map<String, dynamic>;
                      final isSel = item == _selected;
                      final cost = widget.costBuilder != null ? widget.costBuilder!(item) : null;
                      final margin = widget.marginBuilder != null ? widget.marginBuilder!(item) : null;

                      return ListTile(
                        dense: true,
                        selected: isSel,
                        selectedTileColor: MarkaziaColors.orange.withOpacity(0.09),
                        shape: isSel ? const Border(right: BorderSide(color: MarkaziaColors.orange, width: 4)) : null,
                        title: Text(item[widget.titleKey] ?? '',
                            style: TextStyle(
                              fontWeight: isSel ? FontWeight.bold : FontWeight.w600,
                              color: isSel ? MarkaziaColors.orange : MarkaziaColors.dark,
                            )),
                        subtitle: widget.isStaffTab
                            ? Row(
                                children: [
                                  const Icon(Icons.calendar_today_rounded, size: 11, color: Colors.black45),
                                  const SizedBox(width: 4),
                                  Text(widget.subtitleBuilder(item),
                                      style: TextStyle(fontSize: 11, color: isSel ? MarkaziaColors.orange : Colors.grey.shade600)),
                                ],
                              )
                            : Text(widget.subtitleBuilder(item),
                                style: TextStyle(fontSize: 11, color: isSel ? MarkaziaColors.orange : Colors.grey.shade600)),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (cost != null)
                              Text('${cost.toStringAsFixed(2)} د.أ',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: MarkaziaColors.dark)),
                            if (margin != null && margin != 0.0)
                              Text('${(margin * 100).toStringAsFixed(0)}%',
                                  style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: margin >= 0.2 ? Colors.green.shade700 : MarkaziaColors.orange)),
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
        const VerticalDivider(width: 1, thickness: 1, color: Color(0xFFE2E8F0)),
        Expanded(
          child: _selected == null
              ? const Center(child: Text('اختر عنصراً لعرض تفاصيله الكاملة'))
              : Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: widget.detailBuilder(_selected!),
                ),
        ),
      ],
    );
  }
}

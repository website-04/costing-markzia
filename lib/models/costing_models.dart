class SubIngredient {
  final String odooCode;
  final String rmCode;
  final String name;
  final double batchQuantity;
  final String unit;
  final double equivalentQuantity;
  final double costPerUnit;
  final double totalCost;

  SubIngredient({
    required this.odooCode,
    required this.rmCode,
    required this.name,
    required this.batchQuantity,
    required this.unit,
    required this.equivalentQuantity,
    required this.costPerUnit,
    required this.totalCost,
  });

  factory SubIngredient.fromJson(Map<String, dynamic> json) {
    return SubIngredient(
      odooCode: json['odoo_code']?.toString() ?? '',
      rmCode: json['rm_code']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      batchQuantity: (json['batch_quantity'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit']?.toString() ?? '',
      equivalentQuantity: (json['equivalent_quantity'] as num?)?.toDouble() ?? 0.0,
      costPerUnit: (json['cost_per_unit'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class Ingredient {
  final String odooCode;
  final String code;
  final String name;
  final String unit;
  final double quantity;
  final double costPerUnit;
  final double totalCost;
  final bool isSemiFinished;
  final List<SubIngredient> subIngredients;

  Ingredient({
    required this.odooCode,
    required this.code,
    required this.name,
    required this.unit,
    required this.quantity,
    required this.costPerUnit,
    required this.totalCost,
    required this.isSemiFinished,
    required this.subIngredients,
  });

  factory Ingredient.fromJson(Map<String, dynamic> json) {
    var rawSubs = json['sub_ingredients'] as List? ?? [];
    return Ingredient(
      odooCode: json['odoo_code']?.toString() ?? '',
      code: json['code']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      unit: json['unit']?.toString() ?? '',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0.0,
      costPerUnit: (json['cost_per_unit'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
      isSemiFinished: json['is_semi_finished'] == true,
      subIngredients: rawSubs.map((s) => SubIngredient.fromJson(s)).toList(),
    );
  }
}

class MenuItem {
  final String odooCode;
  final String itemCode;
  final String name;
  final String section;
  final String groupName;
  final double markaziyaPrice;
  final double calculatedCost;
  final double profitMargin;
  final List<Ingredient> ingredients;

  MenuItem({
    required this.odooCode,
    required this.itemCode,
    required this.name,
    required this.section,
    required this.groupName,
    required this.markaziyaPrice,
    required this.calculatedCost,
    required this.profitMargin,
    required this.ingredients,
  });

  factory MenuItem.fromJson(Map<String, dynamic> json) {
    var ings = json['ingredients'] as List? ?? [];
    return MenuItem(
      odooCode: json['odoo_code']?.toString() ?? '',
      itemCode: json['item_code']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      section: json['section']?.toString() ?? '',
      groupName: json['group_name']?.toString() ?? '',
      markaziyaPrice: (json['markaziya_price'] as num?)?.toDouble() ?? 0.0,
      calculatedCost: (json['calculated_cost'] as num?)?.toDouble() ?? 0.0,
      profitMargin: (json['profit_margin'] as num?)?.toDouble() ?? 0.0,
      ingredients: ings.map((i) => Ingredient.fromJson(i)).toList(),
    );
  }
}

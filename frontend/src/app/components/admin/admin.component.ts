import { Component, OnInit } from '@angular/core';
import { AdminService, Dish, MissingDish } from '../../services/admin.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  dishes: Dish[] = [];
  missingDishes: MissingDish[] = [];
  showAddDishModal = false;
  loading = false;
  
  // Add dish form
  newDish = {
    dish_name: '',
    country: '',
    ingredients: [{ usda_name: '', weight_g: 100 }]
  };
  
  usdaSearchResults: any[] = [];
  searchingUsda = false;
  currentIngredientIndex = -1;

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadDishes();
    this.loadMissingDishes();
  }

  loadDishes() {
    this.loading = true;
    this.adminService.getDishes().subscribe({
      next: (dishes) => {
        this.dishes = dishes;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading dishes:', err);
        this.loading = false;
      }
    });
  }

  loadMissingDishes() {
    this.adminService.getMissingDishes().subscribe({
      next: (missing) => {
        this.missingDishes = missing;
      },
      error: (err) => {
        console.error('Error loading missing dishes:', err);
      }
    });
  }

  openAddDishModal() {
    this.showAddDishModal = true;
    this.resetForm();
  }

  closeAddDishModal() {
    this.showAddDishModal = false;
    this.resetForm();
  }

  resetForm() {
    this.newDish = {
      dish_name: '',
      country: '',
      ingredients: [{ usda_name: '', weight_g: 100 }]
    };
    this.usdaSearchResults = [];
  }

  addIngredient() {
    this.newDish.ingredients.push({ usda_name: '', weight_g: 100 });
  }

  removeIngredient(index: number) {
    if (this.newDish.ingredients.length > 1) {
      this.newDish.ingredients.splice(index, 1);
    }
  }

  searchUsda(query: string, index: number) {
    if (!query || query.length < 2) {
      this.usdaSearchResults = [];
      return;
    }
    
    this.currentIngredientIndex = index;
    this.searchingUsda = true;
    
    this.adminService.searchUsda(query).subscribe({
      next: (results) => {
        this.usdaSearchResults = results;
        this.searchingUsda = false;
      },
      error: (err) => {
        console.error('Error searching USDA:', err);
        this.searchingUsda = false;
      }
    });
  }

  selectUsdaIngredient(name: string, index: number) {
    this.newDish.ingredients[index].usda_name = name;
    this.usdaSearchResults = [];
    this.currentIngredientIndex = -1;
  }

  submitDish() {
    // Validate
    if (!this.newDish.dish_name || !this.newDish.country) {
      alert('Please fill in dish name and country');
      return;
    }

    if (this.newDish.ingredients.some(i => !i.usda_name || !i.weight_g)) {
      alert('Please fill in all ingredient fields');
      return;
    }

    this.loading = true;
    this.adminService.addDish(this.newDish).subscribe({
      next: (dish) => {
        alert(`Dish "${dish.dish_name}" added successfully!`);
        this.closeAddDishModal();
        this.loadDishes();
      },
      error: (err) => {
        alert(`Error adding dish: ${err.error?.detail || err.message}`);
        this.loading = false;
      }
    });
  }

  useMissing(missing: MissingDish) {
    this.newDish.dish_name = missing.dish_name;
    this.newDish.ingredients = missing.gpt_suggested_ingredients.map(ing => ({
      usda_name: ing,
      weight_g: 100
    }));
    this.showAddDishModal = true;
  }
}
